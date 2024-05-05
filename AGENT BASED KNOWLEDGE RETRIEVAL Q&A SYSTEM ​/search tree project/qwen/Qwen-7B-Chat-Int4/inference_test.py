# import sys
# sys.path.append('/root/sdc1/qwen1.5-4int/qwen/Qwen-7B-Chat-Int4')

# from peft import AutoPeftModelForCausalLM

# def generate_prompt(input):
#   prompt_template = f"""
#     分析用户是不是病人。如果是病人，他会询问如何治疗某种疾病.
#     请根据不同的用户类型回答下面的问题

#     交互格式如下：
#     问题:用户提出的问题，如何治疗某种疾病或者其他类型问题
#     回答:判断用户是不是病人,如果是病人,根据用户提出的问题，进行回答.如果不是,直接输出'<查询数据库>'

#     现在开始：
#     问题:{input}
#     回答:
#   """
#   return prompt_template

# import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer
# from transformers import GenerationConfig
# from qwen_generation_utils import make_context, decode_tokens, get_stop_words_ids
# from peft import AutoPeftModelForCausalLM

# tokenizer = AutoTokenizer.from_pretrained(
#     '/root/sdc1/qwen1.5-4int/model_finetuning',
#     pad_token='<|extra_0|>',
#     eos_token='<|endoftext|>',
#     padding_side='left',
#     trust_remote_code=True
# )

# model = AutoPeftModelForCausalLM.from_pretrained(
#     '/root/sdc1/qwen1.5-4int/model_finetuning',
#     pad_token_id=tokenizer.pad_token_id,
#     device_map="auto",
#     trust_remote_code=True
# ).eval()

# prompt = generate_prompt('精神分裂症导致什么后果？')
# response,_ = model.chat(tokenizer,prompt,history = None)
# print(response)

import sys
sys.path.append('/root/sdc1/qwen1.5-4int/qwen/Qwen-7B-Chat-Int4')

from peft import AutoPeftModelForCausalLM

def generate_prompt(input):
    prompt_template = f"""
    分析用户是不是病人。如果是病人,他会询问如何治疗某种疾病。
    请根据不同的用户类型回答下面的问题
    
    交互格式如下:
    问题:用户提出的问题,如何治疗某种疾病或者其他类型问题 
    回答:判断用户是不是病人,如果是病人,根据用户提出的问题,进行回答。如果不是,直接输出'<查询数据库>'
    
    现在开始:
    问题:{input}
    回答:
    """
    return prompt_template

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import GenerationConfig
from qwen_generation_utils import make_context, decode_tokens, get_stop_words_ids  
from peft import AutoPeftModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained(
    '/root/sdc1/qwen1.5-4int/model_finetuning',
    pad_token='<|extra_0|>',
    eos_token='<|endoftext|>',
    padding_side='left',
    trust_remote_code=True
)

model = AutoPeftModelForCausalLM.from_pretrained(
    '/root/sdc1/qwen1.5-4int/model_finetuning',
    pad_token_id=tokenizer.pad_token_id,
    device_map={"": 2},  # 指定使用 GPU 2
    trust_remote_code=True
).eval()

prompt = generate_prompt('精神分裂症导致什么后果?') 
response, _ = model.chat(tokenizer, prompt, history=None)
print(response)
