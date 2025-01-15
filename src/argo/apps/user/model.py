import pymongo
from pymongo import IndexModel

import logging

from pydantic import Field

from argo.apps.common.model import BaseDocument
from argo.utils.common import get_unique_id


class User(BaseDocument):
    """
    Represents a user account
    """

    id: str = Field(default_factory=get_unique_id)
    name: str = Field(..., description="Display name")
    username: str = Field(..., description="Username")
    description: str = Field("",description=" description")
    user_id: str = Field("",description=" who created this user")
    email: str = Field("",description=" email")
    avatar:str = Field("", description="avatar URL")
    user_type: str = Field("human", description="Type of user,agent or user")
    register_ip: str = Field("", description="register ip")
    details:dict = Field({}, description="Details about user")

    class Settings:
        name = "user"
        use_state_management = True

    @classmethod
    async def get_user_by_device_id(cls, device_id: str):
        return await cls.find_one({"username": device_id})


    @classmethod
    async def create_user_by_device_id(cls,device_id,ip=""):
        doc = await cls.find_one({"username": device_id})
        if doc is None:
            data = {
                "name": device_id,
                "username": device_id,
                "register_ip": ip
            }
            return await cls(**data).create()
        else:
            raise Exception(f"User {device_id} already exists")