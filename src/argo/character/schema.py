from typing import List, Optional, Union
from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class MessageContent(BaseModel):
    text: str
    action: Optional[str] = None

class Message(BaseModel):
    user: str
    content: MessageContent

class StyleConfig(BaseModel):
    all: List[str]=[]
    chat: List[str]=[]
    post: List[str]=[]

class VoiceSettings(BaseModel):
    model: str
    url: str=""
    description: str=""

class TTSSettings(BaseModel):
    model: str
    url: str=""
    description: str=""

class LLMSettings(BaseModel):
    model: str
    api_key: str=""
    base_url: str=""
    temperature:float =Field(default=0.75,ge=0,le=1)
    top_p:float =Field(default=0.75,ge=0,le=1)
    frequency_penalty:float = Field(default=0.9, ge=0, le=2)
    top_k: int = Field(default=5, ge=0, le=80)
    context_round:int=Field(default=2,ge=0,le=10)
    max_resp_length:int = Field(default=500, ge=300, le=4000)
    max_tokens:int = Field(default=1000, ge=1000)
    timeout:int = Field(default=10)
    max_retries:int = Field(default=3)


class Settings(BaseModel):
    secrets: Dict[str, Any] = {}
    llm: LLMSettings=None
    voice: VoiceSettings=None
    tts:TTSSettings=None

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

class KnowledgeItem(BaseModel):
    id: Optional[str] = None
    path: Optional[str] = None
    content: str

class MessageExample(BaseModel):
    user: str
    content: MessageContent

class MessageExamplePair(RootModel):
    root: List[MessageExample]

class Character(BaseModel):
    name: str
    clients: List[str] = Field(default_factory=list)
    model_provider: str = Field(default="OpenAI",alias="modelProvider")
    settings: Optional[Settings] = None
    plugins: List[str] = Field(default_factory=list)
    bio: List[str]
    lore: List[str]
    knowledge: Union[List[str], List[KnowledgeItem], List[Any]] = Field(default_factory=list)
    message_examples: List[List[MessageExample]] = Field(default_factory=list, alias="messageExamples")
    post_examples: List[str] = Field(alias="postExamples")
    topics: List[str]
    style: StyleConfig
    adjectives: List[str] = Field(default_factory=list)

    def get_llm_secret(self):
        pass

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True
        populate_by_name = True
"""
character = Character(
    name="trump",
    modelProvider="openai",
    settings=Settings(
        secrets={},
        voice=VoiceSettings(model="en_US-male-medium")
    ),
    bio=["secured the Southern Border COMPLETELY..."],
    lore=["Democrats using Secret Service..."],
    knowledge=["knows EXACT cost to families..."],
    messageExamples=[[
        Message(
            user="{{user1}}", 
            content=MessageContent(text="What's your stance on abortion?")
        ),
        Message(
            user="trump",
            content=MessageContent(text="EVERYONE KNOWS...")
        )
    ]],
    postExamples=["NO TAX ON TIPS!..."],
    topics=["border security crisis", "Kamala's tax hikes"],
    style=StyleConfig(
        all=["uses FULL CAPS for key phrases..."],
        chat=["directly addresses questioner's concerns..."],
        post=["uses ALL CAPS for key points..."]
    ),
    adjectives=["ILLEGAL", "VIOLENT", "DANGEROUS"]
)
"""