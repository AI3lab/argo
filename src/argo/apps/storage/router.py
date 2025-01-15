import os
import uuid
from datetime import datetime

import aiofiles
from fastapi import UploadFile, APIRouter
from starlette.responses import FileResponse

from argo.apps.common.model import GenericResponse
from argo.env_settings import  settings

router = APIRouter(prefix="/storage", tags=["storage"])
ALLOWED_FILE_EXTENSIONS = [".pdf",".txt",".md",".csv"]


def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1]
    return ext.lower() in ALLOWED_FILE_EXTENSIONS


@router.get("/download/{filename}")
async def download(filename: str):
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(path=filepath, filename=filename)
    else:
        return GenericResponse.error(f"File {filename} not found")


@router.post("/upload")
async def upload(file: UploadFile) -> GenericResponse:
    _, file_extension = os.path.splitext(file.filename)
    file_name = str(uuid.uuid4()) + file_extension

    current_date = datetime.now().strftime("%Y-%m-%d")
    dst_dir = os.path.join(settings.UPLOAD_DIR, current_date)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    file_path = os.path.join(dst_dir, file_name)
    try:
        contents = file.file.read()
        async with aiofiles.open(file_path, 'wb') as fp:
            await fp.write(contents)
    except Exception:
        return GenericResponse.error("There was an error uploading the file")
    finally:
        file.file.close()

    return GenericResponse.success(
        {"name":file_name,"directory":current_date}
    )