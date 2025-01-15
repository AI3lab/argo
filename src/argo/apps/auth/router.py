from fastapi import APIRouter, Depends, Response, HTTPException
from starlette.requests import Request


from argo.apps.auth.schema import DeviceClientSchema
from argo.apps.auth.service import AuthService
from argo.utils.common import get_ip

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login_with_device",  summary="login with device for debug")
async def login_with_device(form: DeviceClientSchema,  request: Request,auth_service: AuthService = Depends()):
    ip = get_ip(request)
    ret = await  auth_service.login_with_device(form.device_id,form.location,ip)
    return ret

