from datasets import load_dataset
from analyzer import *
from llm import *
from report import *

import os
from tempfile import NamedTemporaryFile
import torch

import tokenize
from io import StringIO
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def process_example(code_snippet, label, context_info=None):
    with NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
        tmp.write(code_snippet)
        tmp_path = tmp.name

    bandit_output = run_bandit(tmp_path)

    fim_code = insert_fim_holes(code_snippet, bandit_output)

    context_info = context_info or {"label": label}

    prompt = {
        "code": fim_code,
        "bandit": bandit_output,
        "context": context_info
    }
    review = generate_review(prompt)

    os.remove(tmp_path)

    return {
        "code": code_snippet,
        "label": label,
        "review": review,
        "bandit": bandit_output,
        "context": context_info
    }
    
def sanitize_code(code):
    return re.sub(r'[^\x00-\x7F]+', '', code)
    
def clean_code(code):
    return code.replace("```python", "").replace("```", "").strip()

def remove_comments(code):
    result = []
    tokens = tokenize.generate_tokens(StringIO(code).readline)

    prev_token_type = None
    for token_type, token_string, _, _, _ in tokens:
        if token_type != tokenize.COMMENT:
            if prev_token_type in [tokenize.NAME, tokenize.NUMBER, tokenize.OP] and token_type in [tokenize.NAME, tokenize.NUMBER, tokenize.OP]:
                result.append(" ")
            result.append(token_string)
        prev_token_type = token_type

    return "".join(result).strip()

def clean_code_pipeline(code):
    cleaned = clean_code(code)
    sanitized = sanitize_code(cleaned)
    fully_cleaned_code = remove_comments(sanitized)
    return fully_cleaned_code

def load_python_samples(limit=None):
    raw_dataset = load_dataset("CyberNative/Code_Vulnerability_Security_DPO", split="train")
    python_snippets = []
    
    for example in raw_dataset:
        if example["lang"] == "python":
            fully_cleaned_code = clean_code_pipeline(example["rejected"])
            python_snippets.append({
                "code": fully_cleaned_code,
                "label": example.get("vulnerability", ""),
                "question": example.get("question", "")
            })
            if limit and len(python_snippets) >= limit:
                break
    return python_snippets

def main():
    print("Loading Python-only samples...")
    dataset = load_python_samples(limit=20)

    results = []
    for i, item in enumerate(dataset):
        code_snippet = item["code"]
        label = item["label"]
        context_info = {
            "vulnerability_description": label,
            "prompt_question": item["question"]
        }

        print(f"Analyzing sample {i}...")
        result = process_example(code_snippet, label, context_info)
        results.append(result)

    generate_report(results, out_path="review_report.md")
    print("Review report generated.")

if __name__ == "__main__":
    torch.cuda.is_available()
    main()
