from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Tool(str, Enum):
    claude = "claude"
    openai = "openai"
    gemini = "gemini"
    generic = "generic"


class Prompt(BaseModel):
    id: str = ""
    name: str
    description: str = ""
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    tool: Tool = Tool.generic
    variables: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptListItem(BaseModel):
    id: str
    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    tool: Tool = Tool.generic
    updated_at: datetime


class PromptCreate(BaseModel):
    name: str
    description: str = ""
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    tool: Tool = Tool.generic
    variables: list[str] = Field(default_factory=list)


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    tool: Optional[Tool] = None
    variables: Optional[list[str]] = None


class RenderRequest(BaseModel):
    variables: dict[str, str] = Field(default_factory=dict)
