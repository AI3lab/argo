import asyncio


from argo.client.terminal.terminal_client import TerminalClient


def main():
    SERVER_URL = "ws://localhost:8000/ws"
    UID = "Bob"
    TOKEN = None

    client = TerminalClient(SERVER_URL, UID, TOKEN)

    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\nClient terminated by user")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        print("Client stopped")


if __name__ == "__main__":
    main()