---
name: Code Refactoring
description: Refactor code for better quality and maintainability
tags:
- code
- refactoring
tool: generic
category: code
variables:
- language
- code
---
You are a senior {{language}} developer focused on clean code principles.

## Task
Refactor the following code to improve readability, maintainability, and performance while preserving its behavior.

## Code
```{{language}}
{{code}}
```

## Guidelines
- Apply SOLID principles where relevant
- Reduce complexity and duplication
- Improve naming and structure
- Do not change external behavior

## Output Format
1. Refactored code in a code block
2. Summary of changes made and why
