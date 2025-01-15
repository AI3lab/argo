from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext

from argo.apps.user.model import User
from argo.env_settings import settings


def get_auth_resp(access_token, user):
    data = {
        "user_id": user.id,
        "avatar":user.avatar,
        "user_type":user.user_type,
        "name": user.name,
        "access_token": access_token,
        "token_type": "bearer"
    }
    return data


class AuthService:
    def __init__(self):
        super().__init__()
        self.hasher = CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.jwt_secret_key = settings.JWT_SECRET_KEY
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 60 * 24 * 30
        self.guard = {}



    async def create_access_token(self, uid: str,loc:str="front",expires_delta: timedelta | None = None)->str:

        data = {
            "sub":uid,
            "loc":loc
        }
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        session_id = jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.algorithm)
        return session_id


    async def login_with_device(self,device_id:str,location:str="h5",ip:str="127.0.0.1"):
        user = await User.get_user_by_device_id(device_id)
        if user is None:
            user = await User.create_user_by_device_id(device_id,ip)
            access_token = await self.create_access_token(user.id,location)

        else:
            access_token = await self.create_access_token(user.id,location)
        auth_resp = get_auth_resp(access_token,user)
        return auth_resp







