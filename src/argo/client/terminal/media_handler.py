
import subprocess
import webbrowser
import platform
from pathlib import Path
import tempfile
import requests

from enum import Enum


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class MediaHandler:
    def __init__(self):
        self.system = platform.system().lower()

    def _get_media_player(self):
        if self.system == 'windows':
            return 'start'
        elif self.system == 'darwin':
            return 'open'
        else:
            return 'xdg-open'

    def _download_media(self, url: str) -> str:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                filename = url.split('/')[-1]
                temp_path = Path(tempfile.gettempdir()) / filename

                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                return str(temp_path)
        except Exception as e:
            print(f"Error downloading media: {e}")
        return None

    def handle_media(self, media_resource: dict):
        try:
            local_path = self._download_media(media_resource['url'])
            if local_path:
                player = self._get_media_player()
                subprocess.Popen([player, local_path], shell=True)
        except Exception as e:
            print(f"Error handling media: {e}")

    def handle_link(self, link: dict):
        try:
            webbrowser.open(link['url'])
        except Exception as e:
            print(f"Error opening link: {e}")

