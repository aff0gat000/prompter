---
name: Code Review
description: Review code for bugs, style issues, and improvements
tags:
- code
- review
tool: generic
category: code
variables:
- language
- code
---
You are a senior software engineer conducting a thorough code review.

## Task
Review the following {{language}} code and provide feedback on:
1. **Bugs & Errors** - Logic errors, edge cases, potential runtime failures
2. **Style & Readability** - Naming, formatting, clarity
3. **Performance** - Inefficiencies or unnecessary operations
4. **Security** - Potential vulnerabilities
5. **Suggestions** - Concrete improvements with code examples

## Code to Review
```{{language}}
{{code}}
```

## Output Format
Organize feedback by category. For each issue, reference the relevant line and provide a suggested fix.
