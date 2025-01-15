import asyncio
import websockets
import aioconsole
import signal
import sys
import json
import subprocess
import webbrowser
import platform
from pathlib import Path
import tempfile
import requests
from typing import Optional
from urllib.parse import urlencode
from enum import Enum


class TerminalClient:
    def __init__(self, url: str, uid: str, token: Optional[str] = None):
        self.base_url = url
        self.uid = uid
        self.token = token
        self.ws = None
        self.running = True

    def get_ws_url(self) -> str:
        params = {'token': self.token} if self.token else {}
        query = f"?{urlencode(params)}" if params else ""
        return f"{self.base_url}/{self.uid}{query}"

    async def connect(self):
        url = self.get_ws_url()
        try:
            self.ws = await websockets.connect(url)
            print(f"Connected to {url}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    async def receive_messages(self):
        while self.running:
            try:
                if self.ws:
                    message = await self.ws.recv()
                    print(f"\nReceived: {message}")
                    print("> ", end='', flush=True)  # 重新打印提示符
            except websockets.ConnectionClosed:
                print("\nConnection closed by server")
                self.running = False
                break
            except Exception as e:
                print(f"\nError receiving message: {e}")
                self.running = False
                break

    async def send_message(self, message: str):
        try:
            if self.ws:
                await self.ws.send(message)
        except websockets.ConnectionClosed:
            print("Connection closed by server")
            self.running = False
        except Exception as e:
            print(f"Error sending message: {e}")
            self.running = False

    async def get_input(self):
        while self.running:
            try:
                command = await aioconsole.ainput("> ")
                if command.lower() in ['quit', 'exit']:
                    self.running = False
                    break
                await self.send_message(command)
            except Exception as e:
                print(f"Error reading input: {e}")
                self.running = False
                break

    def handle_signal(self, signum, frame):
        print("\nReceived signal to terminate")
        self.running = False

    async def cleanup(self):
        if self.ws:
            await self.ws.close()
            self.ws = None

    async def run(self):
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        if not await self.connect():
            return

        try:
            receive_task = asyncio.create_task(self.receive_messages())
            input_task = asyncio.create_task(self.get_input())

            await asyncio.gather(receive_task, input_task)
        finally:
            await self.cleanup()

