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