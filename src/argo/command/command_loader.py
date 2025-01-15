import importlib
import yaml
from typing import Dict, Any
from argo.configs import logger


class CommandLoader:
    @staticmethod
    def load_commands(yaml_path: str) -> Dict[str, Any]:
        try:
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)

            commands = {}
            for cmd_name, cmd_config in config.get('commands', {}).items():
                handler_path = cmd_config['handler']
                module_path, class_name = handler_path.rsplit('.', 1)

                try:
                    module = importlib.import_module(module_path)
                    handler_class = getattr(module, class_name)

                    params = cmd_config.get('params', {})

                    if 'description' not in params:
                        params['description'] = cmd_config.get('description', '')

                    try:
                        handler = handler_class(**params)

                        commands[cmd_name] = {
                            'handler': handler,
                            'description': params['description']
                        }

                        logger.info(f"Loaded command: {cmd_name} from {handler_path}")
                    except TypeError as e:
                        logger.error(f"Parameter error for command {cmd_name}: {e}")
                        logger.error(f"Provided params: {params}")
                        continue

                except (ImportError, AttributeError) as e:
                    logger.error(f"Failed to load command {cmd_name}: {e}")
                    continue

            return commands

        except Exception as e:
            logger.error(f"Error loading commands from {yaml_path}: {e}")
            return {}