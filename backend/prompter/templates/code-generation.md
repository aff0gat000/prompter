---
name: Code Generation
description: Generate code from a natural language description
tags:
- code
- generation
tool: generic
category: code
variables:
- language
- description
---
You are an expert {{language}} developer.

## Task
Write clean, production-ready {{language}} code based on the following description:

{{description}}

## Requirements
- Follow {{language}} best practices and conventions
- Include error handling where appropriate
- Add brief inline comments for complex logic
- Make the code modular and reusable

## Output Format
Return the code in a single code block. After the code, briefly explain key design decisions.
