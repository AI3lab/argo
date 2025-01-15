import json
from enum import Enum
from typing import Any, Optional, Generic, T

from pydantic import BaseModel


class EventMessage:
    def __init__(self, evt: str, data: Any):
        self.evt = evt
        self.data = data

    @classmethod
    def from_json(cls, json_str: str) -> "EventMessage":
        try:
            message_dict = json.loads(json_str)
            return cls(
                evt=message_dict.get("evt"),
                data=message_dict.get("data")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON message: {e}")

    def to_json(self) -> str:
        return json.dumps({
            "evt": self.evt,
            "data": self.data
        })



class MessageType(str, Enum):
    SYSTEM = "system"
    CHAT = "chat"
    CHAT_STREAM = "chat_stream"
    COMMAND = "command"
class WebSocketMessage(BaseModel):
    type: MessageType
    content: str
    agent_id: Optional[str] = None
    channel_id: Optional[str] = None
    stream: bool = False
    is_final: bool = False
"""


"""
class IDModel(BaseModel):
    id:str

class GenericResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = ""
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "success") -> "GenericResponse[T]":
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, message: str, code: int = 1) -> "GenericResponse[T]":
        return cls(code=code, message=message)