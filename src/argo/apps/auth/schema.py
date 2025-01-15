from email.policy import default
from typing import List, Optional

from pydantic import BaseModel, Field



class DeviceClientSchema(BaseModel):
    device_id: str
    location:str="h5"
