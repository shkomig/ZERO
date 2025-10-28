---
license: apache-2.0
pipeline_tag: text-generation
language:
  - en
  - he
tags:
- pretrained
inference:
  parameters:
    temperature: 0.7
---

[<img src="https://i.ibb.co/5Lbwyr1/dicta-logo.jpg" width="300px"/>](https://dicta.org.il)

# Adapting LLMs to Hebrew: Unveiling DictaLM 2.0 with Enhanced Vocabulary and Instruction Capabilities

The DictaLM-2.0 Large Language Model (LLM) is a pretrained generative text model with 7 billion parameters trained to specialize in Hebrew text. 

For full details of this model please read our [release blog post](https://dicta.org.il/dicta-lm) or the [technical report](https://arxiv.org/abs/2407.07080).

This is the full-precision base model. 
You can view and access the full collection of base/instruct unquantized/quantized versions of `DictaLM-2.0` [here](https://huggingface.co/collections/dicta-il/dicta-lm-20-collection-661bbda397df671e4a430c27).

## Example Code

```python
from transformers import pipeline
import torch

# This loads the model onto the GPU in bfloat16 precision
model = pipeline('text-generation', 'dicta-il/dictalm2.0', torch_dtype=torch.bfloat16, device_map='cuda')

# Sample few shot examples
prompt = """
עבר: הלכתי
עתיד: אלך

עבר: שמרתי
עתיד: אשמור

עבר: שמעתי
עתיד: אשמע

עבר: הבנתי
עתיד:
"""

print(model(prompt.strip(), do_sample=False, max_new_tokens=8, stop_sequence='\n'))
# [{'generated_text': 'עבר: הלכתי\nעתיד: אלך\n\nעבר: שמרתי\nעתיד: אשמור\n\nעבר: שמעתי\nעתיד: אשמע\n\nעבר: הבנתי\nעתיד: אבין\n\n'}]
```

## Example Code - 4-Bit

There are already pre-quantized 4-bit models using the `GPTQ` and `AWQ` methods available for use: [DictaLM-2.0-AWQ](https://huggingface.co/dicta-il/dictalm2.0-AWQ) and [DictaLM-2.0-GPTQ](https://huggingface.co/dicta-il/dictalm2.0-GPTQ).

For dynamic quantization on the go, here is sample code which loads the model onto the GPU using the `bitsandbytes` package, requiring :

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained('dicta-il/dictalm2.0', torch_dtype=torch.bfloat16, device_map='cuda', load_in_4bit=True)
tokenizer = AutoTokenizer.from_pretrained('dicta-il/dictalm2.0')

prompt = """
עבר: הלכתי
עתיד: אלך

עבר: שמרתי
עתיד: אשמור

עבר: שמעתי
עתיד: אשמע

עבר: הבנתי
עתיד:
"""

encoded = tokenizer(prompt.strip(), return_tensors='pt').to(model.device)
print(tokenizer.batch_decode(model.generate(**encoded, do_sample=False, max_new_tokens=4)))
# ['<s> עבר: הלכתי\nעתיד: אלך\n\nעבר: שמרתי\nעתיד: אשמור\n\nעבר: שמעתי\nעתיד: אשמע\n\nעבר: הבנתי\nעתיד: אבין\n\n']
```


## Model Architecture

DictaLM-2.0 is based on the [Mistral-7B-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1) model with the following changes:
- An extended tokenizer with 1,000 injected tokens specifically for Hebrew, increasing the compression rate from 5.78 tokens/word to 2.76 tokens/word.  
- Continued pretraining on over 190B tokens of naturally occuring text, 50% Hebrew and 50% English.

## Notice

DictaLM 2.0 is a pretrained base model and therefore does not have any moderation mechanisms.

## Citation

If you use this model, please cite:

```bibtex
@misc{shmidman2024adaptingllmshebrewunveiling,
      title={Adapting LLMs to Hebrew: Unveiling DictaLM 2.0 with Enhanced Vocabulary and Instruction Capabilities}, 
      author={Shaltiel Shmidman and Avi Shmidman and Amir DN Cohen and Moshe Koppel},
      year={2024},
      eprint={2407.07080},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2407.07080}, 
}
```