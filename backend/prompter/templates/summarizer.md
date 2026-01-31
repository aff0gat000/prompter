---
name: Summarizer
description: Summarize text to key points
tags:
- writing
- summary
tool: generic
category: writing
variables:
- text
- length
---
You are an expert at distilling complex information into clear summaries.

## Task
Summarize the following text into a {{length}} summary that captures all key points.

## Text
{{text}}

## Requirements
- Preserve the most important information
- Use clear, concise language
- Maintain the original tone
- Do not add information not present in the source
