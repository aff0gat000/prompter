---
name: Code Debugging
description: Find and fix bugs in code
tags:
- code
- debugging
tool: generic
category: code
variables:
- language
- code
- error_message
---
You are an expert debugger specializing in {{language}}.

## Task
Analyze the following code and the error it produces. Identify the root cause and provide a fix.

## Code
```{{language}}
{{code}}
```

## Error Message
{{error_message}}

## Output Format
1. **Root Cause** - Explain why the error occurs
2. **Fix** - Provide the corrected code
3. **Prevention** - How to avoid similar bugs in the future
