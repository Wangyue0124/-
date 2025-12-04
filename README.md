python -m venv venv_project

venv_project\Scripts\activate

python -m pip install torch --index-url https://download.pytorch.org/whl/cu121

pip install bitsandbytes transformers peft datasets accelerate

huggingface-cli login

h_f_PRkBwOZlbbCcWjcaEEdjvLOJeiKhuKdaLc

transformers>=4.45.0

datasets>=3.0.0

peft>=0.13.0

accelerate>=1.0.0

sentencepiece>=0.2.0

pip install -r requirements.txt

python train_all_lora.py
