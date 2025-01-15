# Argo

Multi Agent AI Framework And Application Platform

## Design goals
- Enable agents to collaboratively create deterministic workflow automatically
- Distributed agent collaboration support
- Highly extensible - create your own commands,actions,plugins
- Built-in event system
- Built-in crontab task system
- Web3 Support
- Eliza character schema support

We are in the process of heavy development

## Quick Start

### Prerequisites
- Python 3.10+
- Redis
- MongoDB

### How to use the framework

1. Install Poetry

We use [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) to build this project.


```bash
curl -sSL https://install.python-poetry.org | python3 - --version 1.8.4
...
poetry install
```

2. Install redis and mongodb

Install them according to different operating systems or use Docker for installation.

3. Configure 

Modify the trump.character.json in characters directory.We utilize [OpenRouter](https://openrouter.ai/) to streamline the testing of various models.


```bash
 "llm": {
            "api_key": "",
            "model":"anthropic/claude-3.5-sonnet",
            "base_url": "https://openrouter.ai/api/v1",
            "timeout": 60
        }

```
Copy .env.example to .env and modify it to meet your enviroments

```bash
...
API_HOST=127.0.0.1
API_PORT=8000
API_DEBUG=True

REGISTER_AGENT_TO_RELAY=True #the P2P relay network will launch later

RELAY_SERVER_HOST=doamin  #will launch later
RELAY_SERVER_PORT=8188


DATABASE_TYPE=mongodb
DATABASE_URL=mongodb://localhost:27017/
DATABASE_NAME=ai3lab

REDIS_POOL_MAX_CONNECTIONS = 500
REDIS_POOL_TIMEOUT = 5.0
REDIS_POOL_RETRY_ON_TIMEOUT = True
REDIS_POOL_HEALTH_CHECK_INTERVAL = 30
REDIS_HOST=127.0.0.1
REDIS_PASSWORD=

STORAGE_DOMAIN=http://127.0.0.1:8000

EXTENSION_DIRS=

MPC_WALLET_PATH=wallet  #MPC Wallet support will launch later
MPC_WALLET_SECRET=

JWT_ALGORITHM=HS256

LLM_KEY=
LLM_BASE_URL=
LLM_MODEL=
COMMANDS_YAML_PATH=/deploy/argo/commands.yml #cusomize command,aboluste path 
CHARACTERS_PATH=/deploy/argo/characters/trump.character.json,/deploy/argo/characters/alic.character.json #Multiple characters separated by commas


```
start agent server



4. Start Agent server and client

```bash
import asyncio
import sys

from argo.agent_engine import AgentEngine
from argo.configs import logger

async def main():
    env = sys.argv[1] if len(sys.argv) > 1 else "dev"
    dev_mode = env == "dev"

    try:
        engine = AgentEngine()
        logger.info("Starting Agent Server...")
        engine.start(dev_mode=dev_mode)

    except KeyboardInterrupt:
        logger.info("Shutting Agent Server...")
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

$cd examples
$python main.py

INFO:     Will watch for changes in these directories: ['/home/a/train/argo/example']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [54664] using StatReload
INFO:     Started server process [54666]
INFO:     Waiting for application startup.
2025-01-15 02:51:10 - main.py[line:19] - INFO: Starting up application...
2025-01-15 02:51:10 - runtime_state.py[line:67] - INFO: Worker 54666 starting up...
2025-01-15 02:51:10 - redis_manager.py[line:60] - INFO: Redis connection pool initialized
2025-01-15 02:51:10 - memory_manager.py[line:30] - INFO: DB connection pool initialized
2025-01-15 02:51:10 - event_handler.py[line:27] - INFO: Event handler started
2025-01-15 02:51:10 - runtime_state.py[line:57] - INFO: Loading characters
2025-01-15 02:51:10 - character_manager.py[line:33] - INFO: JSON file is valid against the schema.
2025-01-15 02:51:10 - character_manager.py[line:61] - INFO: Successfully loaded and cached character: trump
2025-01-15 02:51:10 - character_agent.py[line:53] - INFO: init chat handler: anthropic base_url: https://openrouter.ai/api/v1
2025-01-15 02:51:10 - chat_handler.py[line:24] - INFO: init character: anthropic
2025-01-15 02:51:10 - runtime_state.py[line:42] - INFO: Loading commands
2025-01-15 02:51:10 - command_manager.py[line:13] - INFO: Registered help handler <argo.command.commands.HelpCommandHandler object at 0x796bd37789a0>
2025-01-15 02:51:10 - command_manager.py[line:13] - INFO: Registered status handler <argo.command.commands.StatusCommandHandler object at 0x796bd3778e50>
2025-01-15 02:51:10 - command_manager.py[line:13] - INFO: Registered users handler <argo.command.commands.ListUsersCommandHandler object at 0x796bd2d27a90>
2025-01-15 02:51:10 - command_manager.py[line:13] - INFO: Registered msg handler <argo.command.commands.MessageCommandHandler object at 0x796bd2d27bb0>
2025-01-15 02:51:10 - command_manager.py[line:13] - INFO: Registered load_character handler <argo.command.commands.LoadCharacterCommandHandler object at 0x796bd2d27c10>
2025-01-15 02:51:10 - command_manager.py[line:13] - INFO: Registered agents handler <argo.command.commands.ListAgentsCommandHandler object at 0x796bd2d27c70>
2025-01-15 02:51:10 - command_loader.py[line:36] - INFO: Loaded command: mycmd from custom_commands.MyCustomCommand
2025-01-15 02:51:10 - command_manager.py[line:13] - INFO: Registered mycmd handler <custom_commands.MyCustomCommand object at 0x796bd2d27d90>
2025-01-15 02:51:10 - main.py[line:24] - INFO: Available route: /openapi.json [{'GET', 'HEAD'}]
2025-01-15 02:51:10 - main.py[line:24] - INFO: Available route: /docs [{'GET', 'HEAD'}]
2025-01-15 02:51:10 - main.py[line:24] - INFO: Available route: /docs/oauth2-redirect [{'GET', 'HEAD'}]
2025-01-15 02:51:10 - main.py[line:24] - INFO: Available route: /redoc [{'GET', 'HEAD'}]
2025-01-15 02:51:10 - main.py[line:24] - INFO: Available route: /status [{'GET'}]
2025-01-15 02:51:10 - main.py[line:26] - INFO: Available WebSocket route: /ws/{uid}
INFO:     Application startup complete.


```

client connect to server

```bash
$cd examples
$python client1.py 

> /help
> 
Received: Available command:
/agents - List all connected agents
/help - Show help information
/load_character - Load character
/msg - Send private message to user: /msg user_id message
/mycmd - My custom command description
/status - Show current system status
/users - List all connected users

> 


```


Notice: Major updates are expected soon. Please keep watching.



