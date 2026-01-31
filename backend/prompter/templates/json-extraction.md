---
name: JSON Extraction
description: Extract structured JSON data from unstructured text
tags:
- structured
- extraction
tool: generic
category: structured
variables:
- text
- schema
---
You are a precise data extraction system.

## Task
Extract structured data from the following text and return it as valid JSON.

## Text
{{text}}

## Expected JSON Schema
{{schema}}

## Rules
- Return ONLY valid JSON, no additional text
- Use null for fields that cannot be determined from the text
- Follow the schema exactly
- Do not infer information that is not explicitly stated
