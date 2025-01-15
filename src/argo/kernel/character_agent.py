from typing import Dict, Union, AsyncGenerator, Optional, List
import json
from argo.character.schema import Character
from argo.command.commands import CommandContext
from argo.configs import logger
from argo.kernel.chat_handler import ChatHandler
from argo.kernel.schema import GenericResponse


class CharacterAgent:
    def __init__(
            self,
            character:Character
    ):
        self.character = character
        self.name = character.name
        self.model_provider = character.model_provider.lower()
        self.plugins = character.plugins

        # Initialize chat handler
        self.chat_handler = self.init_chat_handler()

        # Build system message
        self.system_message = self._build_system_message()
        self.conversation_history: List[Dict] = []


    def init_chat_handler(self):
        #TODO
        llm_settings = self.character.settings.llm if self.character.settings else None

        api_key = llm_settings.api_key if llm_settings else None
        base_url = llm_settings.base_url if llm_settings else None
        max_tokens = llm_settings.max_tokens if llm_settings else None
        timeout = llm_settings.timeout if llm_settings else None
        max_retries = llm_settings.max_retries if llm_settings else None
        temperature = llm_settings.temperature if llm_settings else None

        kwargs = {}
        if base_url:
            kwargs["base_url"] = base_url
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if timeout:
            kwargs["timeout"] = timeout
        if max_retries:
            kwargs["max_retries"] = max_retries
        if temperature:
            kwargs["temperature"] = temperature



        logger.info(f"init chat handler: {self.model_provider} base_url: {base_url}")
        return ChatHandler(
            model_provider=self.model_provider,
            model_name=llm_settings.model,
            api_key=api_key,
            **kwargs
        )

    def _build_system_message(self) -> str:
        system_message_parts = [
            f"You are {self.character.name}.",
            "\nBiography:",
            *self.character.bio,
            "\nLore:",
            *self.character.lore,
            "\nStyle guidelines:",
            *self.character.style.all,
            "\nChat specific style:",
            *self.character.style.chat,
        ]

        if self.character.adjectives:
            system_message_parts.extend([
                "\nKey characteristics:",
                *[f"- {adj}" for adj in self.character.adjectives]
            ])

        return "\n".join(system_message_parts)

    async def chat(
            self,
            message: str,
            context: CommandContext
    ):
        if not self.conversation_history and self.system_message:
            self.conversation_history.append({
                "role": "system",
                "content": self.system_message
            })

        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        chat_messages = self.chat_handler.convert_to_chat_messages(self.conversation_history)

        response = await self.chat_handler.chat_model.invoke(chat_messages)
        logger.debug(response)
        full_response = response.content
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        return full_response

    async def achat(
            self,
            message: str,
            context: CommandContext
    ) -> AsyncGenerator[str, None]:

        try:
            if not self.conversation_history and self.system_message:
                self.conversation_history.append({
                    "role": "system",
                    "content": self.system_message
                })

            self.conversation_history.append({
                "role": "user",
                "content": message
            })

            chat_messages = self.chat_handler.convert_to_chat_messages(self.conversation_history)

            logger.info(f"chat_messages: {chat_messages}")
            full_response = ""

            async for chunk in self.chat_handler.chat_model.astream(chat_messages):
                chunk_text = chunk.content
                full_response += chunk_text
                logger.info(f"chunk: {chunk}")
                yield chunk_text

            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            logger.error(f"Model API error: {str(e)}")
            yield f"Error: {str(e)}"

    def clear_conversation(self,uid,agent_id):
        pass



class CharacterOutputParser:
    def parse(self, text: str) -> Dict:
        try:
            json_str = text.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        except:
            return {
                "user": "unknown",
                "text": text,
                "action": "speak"
            }


