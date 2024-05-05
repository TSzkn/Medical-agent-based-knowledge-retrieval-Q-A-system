import sys
sys.path.append('/root/sdc1/qwen1.5-4int/qwen/Qwen-7B-Chat-Int4')

from fastapi import FastAPI
from pydantic import BaseModel
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

app = FastAPI()

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
    device_map={"": 2},
    trust_remote_code=True
).eval()

class InputText(BaseModel):
    text: str

@app.post("/generate")
async def generate(input_text: InputText):
    prompt = generate_prompt(input_text.text)
    response, _ = model.chat(tokenizer, prompt, history=None)
    return {"generated_text": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
