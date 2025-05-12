from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.__version__)

tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-1.3b-base", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/deepseek-coder-1.3b-base",
    trust_remote_code=True,
    device_map="auto",
    torch_dtype="auto"
)

def make_prompt(prompt_obj):
    return f"""<｜fim▁begin｜>
{prompt_obj['code']}
<｜fim▁end｜>"""

def generate_review(prompt_obj):
    prompt = make_prompt(prompt_obj)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=512)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

