
from pydantic import BaseModel, Field, HttpUrl, ConfigDict




class UserSchema(BaseModel):
    """
    Represents a user account
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: str = Field(..., description="user id")
    nickname: str = Field(..., description="Display name")
    username: str = Field(..., description="Username")
    address: str = Field("",description="blockchain address")
    email: str = Field("",description=" email")
    avatar:str = Field("", description="avatar URL")
    user_type: str = Field("agent", description="Type of user,agent or user")
    invite_code:  str = Field(default="", max_length=64)
