import torch
from dataclasses import dataclass
from typing import Dict, Any
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# =========================================================
# 設定區
# =========================================================

# 修改：這裡改成 Llama 3.1 70B Instruct
MODEL_ID = "meta-llama/Meta-Llama-3.1-70B-Instruct"

# 訓練資料路徑
DATA_PATH = "all_sft.jsonl"

# 輸出路徑
OUTPUT_DIR = "./llama-3.1-70b-lora"

# =========================================================
# 特殊符號與處理函數
# =========================================================

@dataclass
class SpecialTokens:
    bos: str = "<s>"
    eos: str = "</s>"
    instruction_start: str = "<instruction>\n"
    instruction_end: str = "\n</instruction>\n"
    input_start: str = "<input>\n"
    input_end: str = "\n</input>\n"
    response_start: str = "<response>\n"
    response_end: str = "\n</response>"

TOKENS = SpecialTokens()

def build_text(example: Dict[str, Any]) -> str:
    instruction = example["instruction"]
    input_part = example.get("input", "")
    output_part = example["output"]

    text = (
        TOKENS.bos
        + TOKENS.instruction_start
        + instruction
        + TOKENS.instruction_end
        + TOKENS.input_start
        + (input_part if isinstance(input_part, str) else str(input_part))
        + TOKENS.input_end
        + TOKENS.response_start
        + (output_part if isinstance(output_part, str) else str(output_part))
        + TOKENS.response_end
        + TOKENS.eos
    )
    return text

# =========================================================
# 主程式
# =========================================================

def main():
    use_cuda = torch.cuda.is_available()
    print("use_cuda:", use_cuda, "device_count:", torch.cuda.device_count())

    # 1. 讀取資料集
    dataset = load_dataset("json", data_files=DATA_PATH)["train"]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize_fn(example):
        text = build_text(example)
        tokens = tokenizer(
            text,
            truncation=True,
            # 80GB 顯存足夠處理更長的 context，建議設為 2048 或 4096
            max_length=2048, 
        )
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens

    tokenized = dataset.map(
        tokenize_fn,
        remove_columns=dataset.column_names,
    )

    # 2. 設定 4-bit 量化 (QLoRA) - 70B 必備
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16, # A100/H100 必開 BF16
        bnb_4bit_use_double_quant=True,
    )

    # 3. 載入模型
    print(f"Loading model: {MODEL_ID}...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        # Windows 環境下避免使用 Flash Attention 2，以免安裝失敗
        # attn_implementation="flash_attention_2"
    )

    # 啟用梯度檢查點 (Gradient Checkpointing) 省顯存
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    # 4. 設定 LoRA
    # 針對 70B 模型，建議 train 全層以獲得最佳效果
    lora_config = LoraConfig(
        r=64,
        lora_alpha=128,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj", 
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 5. 訓練參數
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,  # 80GB 顯存通常可開 2~4
        gradient_accumulation_steps=8,  # 累積梯度
        learning_rate=1e-4,             # QLoRA 常用 1e-4
        num_train_epochs=3,
        
        # 專業顯卡設定
        bf16=True,      # A100/H100 建議開啟
        fp16=False,
        
        optim="paged_adamw_32bit",      # 節省顯存的優化器
        logging_steps=5,
        save_steps=50,
        save_total_limit=2,
        report_to="none",               # 關閉 wandb
        ddp_find_unused_parameters=False,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized,
    )

    print("Start training...")
    trainer.train()
    
    print(f"Saving model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Training finished.")

if __name__ == "__main__":
    main()