import os
import wandb
from transformers import GPT2LMHeadModel, GPT2Tokenizer

special_tokens_dict = {'bos_token': '<BOS>',
                       'eos_token': '<EOS>',
                       'pad_token': '<PAD>'}

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer.add_special_tokens(special_tokens_dict)
model.resize_token_embeddings(len(tokenizer))

wandb.login(key="9aa145803699f2aa674faf6be69c8ab904438798")

command = "python transformers/examples/pytorch/language-modeling/run_clm.py \
    --output_dir=model \
    --model_type=gpt2 \
    --model_name_or_path=gpt2 \
    --logging_first_step \
    --do_train \
    --train_file=data/train.txt \
    --do_eval \
    --validation_file=data/valid.txt \
    --per_device_train_batch_size=5 \
    --per_device_eval_batch_size=5 \
    --evaluation_strategy epoch \
    --logging_steps 2000 \
    --save_steps 2000 \
    --save_total_limit 20 \
    --learning_rate 5e-5 \
    --num_train_epochs=2 \
    --overwrite_output_dir"

os.system(command)
