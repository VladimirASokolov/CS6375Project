# Automated Security-Oriented Code Review via Static Analysis and Language Models

## Abstract
This work builds on key concepts from static code analysis and generative language modeling. Static analyzers like Bandit detect known vulnerability patterns in source code. Large language models, particularly those trained on code, can generate code completions and replacements, but require structured prompts and often lack domain-specific knowledge. The integration of these tools presents both implementation and conceptual challenges.

## Introduction
As software systems grow in complexity and scale, automated methods for detecting and remediating security vulnerabilities become increasingly valuable. Static analysis tools are widely used to identify known vulnerability patterns in code, but their rigid rule-based design limits their adaptability. Meanwhile, LLMs trained on large corpora of source code demonstrate promising capabilities in code generation and reasoning. This project aims to bridge these two techniques by using a static analyzer to identify insecure segments and then prompting an LLM to regenerate those segments in a more secure form. The core hypothesis is that this combination can enable more context-aware and adaptable security fixes than either method alone.

## Background
Static code analysis refers to examining source code without executing it, typically to identify bug patterns or potential vulnerabilities. Tools like Bandit specialize in scanning Python code for common issues such as insecure function calls or improper use of user input. However, these tools often lack the ability to suggest fixes or adapt to complex contexts. On the other hand, large language models such as DeepSeek Coder are trained on billions of lines of code and can generate, refactor, or complete code based on textual prompts. When given sufficient context, these models can sometimes infer developer intent and propose syntactically valid and semantically meaningful solutions. Integrating these two approaches allows the static tool to act as a filter and problem identifier, while the LLM acts as a code generator aimed at security-conscious completion.

## Related Work
Combining Large Language Models with Static Analyzers for Code Review Generation proposes a hybrid approach that enhances automated code review by integrating structured static analysis with LLM reasoning [1]. Their system improves review completeness using retrieval-augmented generation (RAG). While our method focuses on security and directly fixing code, their method is focused on general code review.

IRIS: LLM-Assisted Static Analysis for Detecting Security Vulnerabilities introduces IRIS, a neuro-symbolic approach that enhances static vulnerability detection using LLMs and CodeQL [2]. IRIS mines taint specifications for third-party APIs, improving detection accuracy and reducing false positives. While IRIS focuses on whole-repository search starting with a specific vulnerability, our method is interested in simple code snippets and general security issues. 

## Problem Definition
Given a code snippet containing known security vulnerabilities, the system should:
Identify vulnerable lines using a static analyzer.
Remove or mask those lines.
Prompt an LLM to regenerate the removed code with a secure alternative.
Evaluate whether the generated output eliminates the original vulnerability while maintaining functionality.

This problem is challenging because the LLM must understand both the context and intent of the surrounding code without access to the original vulnerable implementation. In addition, static analyzers may miss some vulnerabilities or produce false positives, affecting prompt quality.


## Examples
```python
import os

def evaluate_input ( user_input ) :


    return eval ( user_input )

def main ( ) :
    user_input = input ("Enter some Python code to execute: ")
result = evaluate_input ( user_input )
print ("Result:", result )

if __name__ =="__main__":
    main ( )
```
_Raw Dataset Sample Code: Illustrates an unprocessed code snippet before any cleaning steps are applied, including potential formatting inconsistencies, comments, or non-ASCII characters._

Bandit Report
{'line_number': 6, 'description': 'Use of possibly insecure function - consider using safer ast.literal_eval.'}
_Bandit’s Security Analysis Output: Presents Bandit’s findings, highlighting specific line numbers. Includes a short vulnerability description to aid in manual review, but this explanation is excluded from the LLM input to prevent bias._

LLM Code Review
<｜fim▁begin｜>
import os

def evaluate_input ( user_input ) :


<｜fim▁hole｜>

def main ( ) :
    user_input = input ("Enter some Python code to execute: ")
result = evaluate_input ( user_input )
print ("Result:", result )

if __name__ =="__main__":
    main ( )
<｜fim▁end｜>    return eval ( user_input )
_LLM Response: Structured Code Review & Refinement: Displays the marked prompt used for LLM inference, along with the suggested improvements or fixes generated._

Context
{'vulnerability_description': "Python's built-in function `eval()` can lead to arbitrary code execution if used improperly.", 'prompt_question': 'Write a python code that takes user input as Python code and executes it using the built-in `eval()` function. The executed code should be sanitized to prevent arbitrary code execution.'}
_Contextual Information in Report for Manual Review: Demonstrates additional metadata included in the review report for human oversight. This context is not sent to the LLM._

## Approach
The overall workflow is as follows:
Load Python code samples from a security-focused dataset.
Clean the code by removing markdown, comments, and non-ASCII characters.
Use Bandit to analyze each sample and identify vulnerable lines.
Replace each vulnerable segment with a marker.
Construct a prompt that includes the remaining code and the marker.
Send the prompt to an LLM (DeepSeek Coder 1.3B).
Collect and format the LLM's output.
Compare the result against the reference secure implementation.

This approach is designed to simulate an automated review and repair pipeline, where human intervention is minimal and the system handles both detection and generation.

## Implementation
The system is written in Python and divided into four modules:
Main handles dataset loading and preprocessing.
Analyzer interfaces with Bandit and extracts the list of flagged lines.
LLM formats the prompt and interacts with the DeepSeek Coder model.
Report generates output files that include the original code, Bandit findings, the generated code, and ground-truth reference.

The dataset used is the CyberNative Code_Vulnerability_Security_DPO dataset from Hugging Face, chosen for its annotated examples of secure and insecure Python code. DeepSeek Coder 1.3B was selected for its support for code-specific prompting and insertion tasks. While the model lacks general-purpose reasoning capabilities compared to larger LLMs like GPT-4, it is efficient and easier to deploy locally.

## Evaluation
The system was evaluated on the first 20 samples from the dataset. Each result was manually reviewed and categorized into one of three groups:
Wrong (9/20): The output did not remove the vulnerability or introduced other issues.
Vulnerable (7/20): The generated code closely resembled the original insecure code.
Analyzer Failure (4/20): Bandit failed to detect the vulnerability or flagged unrelated code.

Notably, no cases resulted in a correct and secure replacement. This reveals challenges in both detection accuracy and prompt engineering. The LLM often lacked sufficient context to infer the correct fix, and Bandit's coarse output made it difficult to isolate precise problem areas.

## Discussion
Limitations:
Model size: DeepSeek 1.3B may lack reasoning capacity for nuanced vulnerabilities.
Model choice: A general-purpose model (e.g., GPT-4) with full-text context might have outperformed.
Evaluation scope: Limited to 20 samples, evaluated manually.
Prompt limitations: Removing only flagged lines left flawed surrounding context.
Security understanding: Model lacks explicit training on secure coding practices.

Future Directions:
Integrate vulnerability descriptions directly into prompts
Use larger or fine-tuned LLMs
Expand evaluation to larger test sets with automated scoring
Explore bidirectional prompts (more context before/after hole)

## Conclusion and Future Work
This project explored the use of static analysis to inform LLM-based code repairs. While the combination of Bandit and DeepSeek Coder offers a novel path toward automated, security-focused code review, results showed that significant improvements are needed in prompt engineering, model selection, and evaluation. Future work should explore richer prompts, larger models, and hybrid approaches that include symbolic reasoning or contextual metadata.

## References
[1] I. Jaoua, O. Ben Sghaier, and H. Sahraoui, "Combining Large Language Models with Static Analyzers for Code Review Generation," arXiv:2502.06633v1 [cs.SE], 2025.  

[2] Z. Li, S. Dutta, and M. Naik, "IRIS: LLM-Assisted Static Analysis for Detecting Security Vulnerabilities," arXiv:2405.17238v3 [cs.CR], 2025.

