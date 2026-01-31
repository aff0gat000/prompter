---
name: Classification
description: Classify text into predefined categories
tags:
- structured
- classification
tool: generic
category: structured
variables:
- text
- categories
---
You are a precise text classification system.

## Task
Classify the following text into one of the provided categories.

## Text
{{text}}

## Categories
{{categories}}

## Output Format
Return a JSON object with:
- "category": the chosen category
- "confidence": "high", "medium", or "low"
- "reasoning": brief explanation for the classification

## Rules
- Choose exactly one category
- If none fit well, choose the closest match and set confidence to "low"
