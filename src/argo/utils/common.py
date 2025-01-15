from starlette.requests import Request
from ulid import ULID


def get_unique_id():
    return str(ULID())

def get_ip(request: Request):
    client_host = request.headers.get("X-Forwarded-For")
    if client_host:
        return client_host
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    else:
        return request.client.host