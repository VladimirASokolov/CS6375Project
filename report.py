def generate_report(results, out_path="review.md"):
    with open(out_path, "w", encoding="utf-8") as f:
        for i, res in enumerate(results):
            f.write(f"# Review {i+1}\n\n")
            f.write("```python\n" + res["code"] + "\n```\n\n")
            f.write("## Bandit Report\n")
            f.write("\n\n".join(map(str, res["bandit"])) + "\n\n")
            f.write("## LLM Code Review\n")
            f.write(res["review"] + "\n\n---\n\n")
            f.write("## Context\n")
            f.write(str(res["context"]) + "\n\n---\n\n")