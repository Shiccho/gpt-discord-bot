from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from pydantic import BaseModel
from typing import Any
import json

from openai.types.beta.assistant import Assistant as OpenAIAssistant

from src.constants import DEFAULT_MODEL

logger = logging.getLogger(__name__)


@dataclass
class AssistantCreate:
    name: str
    model: str = DEFAULT_MODEL
    description: str | None = None
    instructions: str | None = None
    tools: list[dict[str, Any]] | None = None
    tool_resources: dict[str, dict[str, list[str]]] | None = None
    metadata: dict[str, str] | None = None

    def input_to_api_create(self) -> dict[str, str]:
        """Convert the AssistantCreate object to dict for input to API create"""
        data = asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
        return data


@dataclass
class Assistant(BaseModel):
    id: str
    created_at: int | None = None
    name: str | None = None
    description: str | None = None
    model: str | None = None
    instructions: str | None = None
    tools: list[dict[str, Any]] | None = None
    tool_resources: dict[str, dict[str, list[str|None]]|None] | None = None

    def input_to_api_update(self) -> dict[str, str]:
        """Convert the Assistant object to dict for input to API update"""
        tmp = asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
        # id is required with the key "assistant_id" for update
        tmp["assistant_id"] = tmp.pop("id")
        # created_at is not needed for update
        remove_keys = ["created_at"]
        for key in remove_keys:
            if key in tmp:
                del tmp[key]
        return tmp

    def render(self) -> str:
        """Render the Assistant object to string to display in discord"""
        return f"[{self.id}] {self.name} - {self.description}"

    @classmethod
    def from_api_output(cls, api_output: OpenAIAssistant) -> None:
        """Create an instance from the OpenAIAssistant object
        - Convert the OpenAIAssistant object to dict
        - Remove the key "object" from the dict
        """
        data = api_output.model_dump(exclude={
            "object",
            "top_p",
            "tempreture", 
            "metadata",
            "response_format",
        })
        
        # Convert the 'tools' to a list of dict
        if 'tools' in data:
            data['tools'] = json.loads(json.dumps(data['tools']))

        return cls.model_validate(data)
