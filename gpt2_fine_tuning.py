import torch
import wandb
import os
from transformers import GPT2LMHeadModel, GPT2Tokenizer

os.environ["TOKENIZERS_PARALLELISM"] = "true"
device = 'cuda' if torch.cuda.is_available() else 'cpu'

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2", low_cpu_mem_usage=True)
model.to(device)

prompt = """Instruction: Generate a Python function that checks if number is a palindrome.

Answer: """
input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

generated_ids = model.generate(input_ids,
                               do_sample=True,
                               temperature=0.9,
                               max_length=64)
generated_text = tokenizer.decode(generated_ids[0])
print(generated_text)

with open('api_keys/wandb.txt') as f:
    key = f.readlines()
wandb.login(key=key[0])

command = 'python transformers/examples/pytorch/language-modeling/run_clm.py \
    --output_dir=model \
    --model_type gpt2 \
    --model_name_or_path=gpt2 \
    --do_train \
    --do_eval \
    --train_file=data/train.txt \
    --validation_file=data/valid.txt \
    --per_device_train_batch_size=1 \
    --per_device_eval_batch_size=1 \
    --evaluation_strategy epoch \
    --logging_steps 300 \
    --save_steps 1500 \
    --save_total_limit 1 \
    --learning_rate 5e-5 \
    --num_train_epochs=1 \
    --overwrite_output_dir'

os.system(command)
