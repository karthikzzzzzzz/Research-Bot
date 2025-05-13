from pydantic import BaseModel
from typing import Annotated, Optional
from typing_extensions import TypedDict
from uuid import UUID
from langgraph.graph.message import add_messages

class Request(BaseModel):
    text: str

class State(TypedDict):
    messages:Annotated[list,add_messages]