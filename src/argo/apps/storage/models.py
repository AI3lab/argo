from pydantic import Field

from argo.apps.common.model import BaseDocument
from argo.utils.common import get_unique_id

class StorageFile(BaseDocument):
    id:str=Field(default_factory=get_unique_id)
    user_id:str=""
    filehash: str=""
    filename: str
    size: int=0
    content_type: str
    filepath:str=""
    file_ext:str=""
    file_type:str=""
    status:int=0
    url:str=""
    is_private:bool=False

    class Settings:
        name = "storage_file"
