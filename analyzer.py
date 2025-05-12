import subprocess
import json

def insert_fim_holes(code: str, bandit_results: list) -> str:
    lines = code.splitlines()
    lines_to_replace = set()

    for issue in bandit_results:
        line_range = issue.get("line_range", [issue["line_number"]])
        for line_num in line_range:
            lines_to_replace.add(line_num)

    lines_to_replace = sorted(lines_to_replace)

    modified_lines = []
    i = 1
    while i <= len(lines):
        if i in lines_to_replace:
            modified_lines.append("<｜fim▁hole｜>")
            while i in lines_to_replace:
                i += 1
        else:
            modified_lines.append(lines[i - 1])
            i += 1

    return "\n".join(modified_lines)

def run_bandit(file_path):
    result = subprocess.run(["bandit", "-f", "json", file_path], capture_output=True, text=True)
    
    try:
        bandit_output = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Failed to parse Bandit output."}

    filtered_results = []
    
    for issue in bandit_output.get("results", []):
        filtered_results.append({
            "line_number": issue["line_number"],
            "description": issue["issue_text"]
        })
    
    return filtered_results