from dataclasses import dataclass
from typing import Dict, Any

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model

MODEL_ID = "meta-llama/Llama-3.2-1B"
DATA_PATH = "all_sft.jsonl"
OUTPUT_DIR = "./multi-lora"


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


def main():
    use_cuda = torch.cuda.is_available()
    print("use_cuda:", use_cuda, "device_count:", torch.cuda.device_count())

    # 1. 讀合併後的 SFT 資料
    dataset = load_dataset("json", data_files=DATA_PATH)["train"]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize_fn(example):
        text = build_text(example)
        tokens = tokenizer(
            text,
            truncation=True,
            max_length=1024,
        )
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens

    tokenized = dataset.map(
        tokenize_fn,
        remove_columns=dataset.column_names,
    )

    # 2. 載 base model（訓練階段不要玩 device_map）
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if use_cuda else torch.float32,
    )

    # 3. 套 LoRA
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    if use_cuda:
        model.to("cuda")

    # 4. 設訓練參數
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        num_train_epochs=3,
        fp16=use_cuda,
        bf16=False,
        dataloader_pin_memory=use_cuda,
        logging_steps=10,
        save_steps=500,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized,
    )

    trainer.train()
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Multi-task LoRA 模型已存到 {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
