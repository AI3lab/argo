import json
import time

from typing import TypeVar, Generic, Optional, List, Any, Union, Dict, Callable, Type

import asyncio


import math

from beanie import Document, Indexed, SortDirection

from argo.configs import logger
from argo.kernel.schema import GenericResponse
from argo.utils.common import get_unique_id
from argo.utils.time import  get_now_ms

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class TimeStampedDocument(Document):
    id: str = Field(default_factory=get_unique_id)
    created_at: int = Field(default_factory=get_now_ms)
    updated_at: Optional[int] = Field(default=0)

    class Settings:
        use_state_management = True
        validate_on_save = True

    async def save(self, *args, **kwargs) -> T:
        self.updated_at = int(time.time_ns() // 1_000_000)
        return await super().save(*args, **kwargs)



class BaseDocument(TimeStampedDocument):

    @classmethod
    async def get_list(
            cls,
            query: Dict = None,
            options: Dict = None,
            callback: Optional[Callable] = None,
            is_async_callback: bool = False,
            user_args: Dict = None
    ):
        ret = await  cls.get_page(query,options,callback,is_async_callback,user_args)
        return ret.data['list']

    @classmethod
    async def get_page(
            cls,
            query: Dict = None,
            options: Dict = None,
            callback: Optional[Callable] = None,
            is_async_callback: bool = False,
            user_args: Dict = None
    ) ->GenericResponse:
        """
        """
        try:
            query = query or {}
            user_args = user_args or {}

            default_options = {
                'page': 1,
                'pagesize': 10,
                'sort': {"_id": SortDirection.DESCENDING}
            }
            options = {**default_options, **(options or {})}

            options['page'] = int(options['page'])
            options['pagesize'] = int(options['pagesize'])

            if options['page'] < 1:
                options['page'] = 1
            if options['pagesize'] < 1:
                options['pagesize'] = 10
            if options['pagesize'] > 100:
                options['pagesize'] = 100

            skip = (options['page'] - 1) * options['pagesize']

            total = await cls.find(query).count()
            total_pages = math.ceil(total / options['pagesize'])

            find_query = cls.find(query)

            if isinstance(options.get('sort'), dict):
                for field, direction in options['sort'].items():
                    find_query = find_query.sort((field, direction))

            objects = await find_query.skip(skip).limit(options['pagesize']).to_list()

            if callback is not None:
                if is_async_callback:
                    objects = await asyncio.gather(*[callback(obj, **user_args) for obj in objects])
                else:
                    objects = [callback(obj, **user_args) for obj in objects]

            out = {
                "total": total,
                "total_page": total_pages,
                "pagesize": options['pagesize'],
                "list": objects
            }
            return GenericResponse.success(out)


        except Exception as e:
            logger.error(f"Error in get_list: {str(e)}")
            raise

    @classmethod
    def add_timestamp(cls, update_dict: Dict) -> Dict:
        if isinstance(update_dict, dict):
            if "$set" not in update_dict:
                update_dict["$set"] = {}
            update_dict["$set"]["updated_at"] = int(time.time_ns() // 1_000_000)
        return update_dict

    async def update(self, *args, **kwargs):
        if args:
            args = (self.add_timestamp(args[0]),) + args[1:]
        return await super().update(*args, **kwargs)

    @classmethod
    async def update_one(cls, *args, **kwargs):
        if args:
            args = (cls.add_timestamp(args[0]),) + args[1:]
        return await super().update_one(*args, **kwargs)

    @classmethod
    async def update_many(cls, *args, **kwargs):
        if args:
            args = (cls.add_timestamp(args[0]),) + args[1:]
        return await super().update_many(*args, **kwargs)

    @classmethod
    async def create_item(cls, data: Dict) -> GenericResponse:
        try:
            item = cls(**data)
            await item.insert()
            return GenericResponse.success(data=item)
        except Exception as e:
            logger.error("Error creating/updating item", exc_info=True)
            return GenericResponse.error(str(e))

    @classmethod
    async def update_item(cls, id: str, data: Dict) -> GenericResponse:

        try:
            item = await cls.get(id)
            if not item:
                return GenericResponse.error("Item not found")

            await item.update({"$set": data})
            return GenericResponse.success(data=item)
        except Exception as e:
            return GenericResponse.error(str(e))





class OpLog(BaseDocument):
    id: str = Field(default_factory=get_unique_id)
    who:str
    operation:str
    message: str
    extra: Any=None

    @classmethod
    async def record(cls,message,who:str="0",operation="",extra=None):
        data = {
            "who":who,
            "message":message,
            "operation":operation,
            "extra":json.dumps(extra),
        }
        await OpLog(**data).create()

    class Settings:
        name = "oplog"


