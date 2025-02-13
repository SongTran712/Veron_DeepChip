from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, AutoConfig
import torch
# Load the DeepSeek-R1 model and tokenizer
model_name = "deepseek-ai/DeepSeek-R1"

config = AutoConfig.from_pretrained("deepseek-ai/DeepSeek-R1", trust_remote_code=True)
del config.quantization_config

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, config = config)

prompt = "Hello world"

inputs = tokenizer.encode(prompt, return_tensors="pt")

with torch.no_grad():
    outputs = model.generate(
        inputs,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        max_new_tokens=1000,
        # early_stopping=True,

    )

# Decode the output
response = tokenizer.decode(outputs[0], skip_special_tokens=True)  # Decode the first output
print(response)
