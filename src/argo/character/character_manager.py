import asyncio
import json
from typing import Dict, Optional, Tuple
from jsonschema import validate
from importlib import resources

from pydantic import ValidationError

from argo.character.schema import Character
from argo.configs import logger
from argo.kernel.character_agent import CharacterAgent


class CharacterManager:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.characters: Dict[str, Character] = {}
        self.agents: Dict[str, CharacterAgent] = {}

        with resources.open_text("argo.character", "character.schema.json") as schema_file:
            self.schema = json.load(schema_file)

        # with open('character.schema.json', 'r') as schema_file:
        #     self.schema = json.load(schema_file)

    def check_character(self, character_file):
        with open(character_file, 'r') as json_file:
            json_data = json.load(json_file)
        try:
            #TODO:CHECK,the schema file needs to be improved to meet the production needs
            # validate(instance=json_data, schema=self.schema)

            logger.info('JSON file is valid against the schema.')
            return json_data
        except:
            logger.error(f'JSON file is not valid against the schema')
            return None

    async def load_character(self, filepath: str) -> Tuple[bool, Optional[Character],str]:

        async with self._lock:
            json_data = self.check_character(filepath)
            if  json_data is None:
                error = f"Invalid character configuration in {filepath}"
                logger.error(error)
                return False,None,error

            try:
                character = Character(**json_data)
            except ValidationError as e:
                error = f"Invalid character configuration{e}"
                logger.error(error)
                return False,None,error

            if character.name in self.characters:
                error = f"Character with name '{character.name}' already exists"
                logger.error(error)
                return False, None, error

            self.characters[character.name] = character
            logger.info(f"Successfully loaded and cached character: {character.name}")
            await self.init_character_agent(character)

            return True,character,"success"

    async def init_character_agent(self,character:Character):
        agent = CharacterAgent(character)
        self.agents[character.name] = agent

    async def get_agent(self, name: str) -> CharacterAgent:

        async with self._lock:
            if name not in self.agents:
                raise KeyError(f"Agent '{name}' not found")
            return self.agents[name]

    async def get_character(self, name: str) -> Character:

        async with self._lock:
            if name not in self.characters:
                raise KeyError(f"Character '{name}' not found")
            return self.characters[name]

    async def remove_character(self, name: str) -> None:
        async with self._lock:
            if name not in self.characters:
                raise KeyError(f"Character '{name}' not found")
            del self.characters[name]
            logger.info(f"Character '{name}' removed from cache")

    async def list_characters(self) -> list[str]:

        async with self._lock:
            return list(self.characters.keys())

    async def clear_cache(self) -> None:
        async with self._lock:
            self.characters.clear()
            logger.info("Character cache cleared")