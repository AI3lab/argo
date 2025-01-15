from typing import Optional, List, Dict, Union, AsyncGenerator

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from argo.configs import logger
from argo.utils.llm import get_chat_model


class ChatHandler:

    def __init__(
            self,
            model_provider: str,
            model_name: Optional[str] = None,
            api_key: Optional[str] = None,
            **kwargs
    ):
        self.model_provider = model_provider.lower()
        self.model_name = model_name
        self.api_key = api_key
        self.kwargs = kwargs
        logger.info(f"init character: {self.model_provider}")
        self.chat_model = self.get_chat_model()
        self.conversation_history: List[Dict] = []

    def get_chat_model(self) -> BaseChatModel:
        if self.model_provider == "openai":
            return ChatOpenAI(
                model_name=self.model_name or "gpt-3.5-turbo",
                openai_api_key=self.api_key,
                **self.kwargs
            )
        elif self.model_provider == "anthropic":
            return ChatOpenAI(
                model_name=self.model_name or "claude-3-5-sonnet-20240620",
                openai_api_key=self.api_key,
                **self.kwargs
            )

        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")

    def convert_to_chat_messages(self, messages: List[Dict[str, str]]):
        chat_messages = []
        for message in messages:
            if message["role"] == "system":
                chat_messages.append(SystemMessage(content=message["content"]))
            elif message["role"] == "user":
                chat_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                chat_messages.append(AIMessage(content=message["content"]))
        return chat_messages



