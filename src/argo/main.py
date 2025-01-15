import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIWebSocketRoute
from starlette.responses import JSONResponse

from argo.kernel.schema import GenericResponse
from argo.kernel.runtime_state import runtime

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(instance: FastAPI):
    try:
        logger.info("Starting up application...")
        await runtime.startup(instance)

        for route in instance.routes:
            if hasattr(route, 'methods'):  # HTTP routes
                logger.info(f"Available route: {route.path} [{route.methods}]")
            elif isinstance(route, APIWebSocketRoute):  # WebSocket routes
                logger.info(f"Available WebSocket route: {route.path}")
            else:  # Other route types
                logger.info(f"Available route: {route.path}")
        yield
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise
    finally:
        logger.info("Shutting down application...")
        try:
            await runtime.shutdown()
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
        finally:
            logger.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan)







@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=200,
        content={"code": exc.status_code, "message": exc.detail}
    )



@app.exception_handler(Exception)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": exc.error}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=200,
        content={"code": 400, "message": "Validation error", "data": exc.errors()}
    )


@app.get("/status")
async def get_status():
    worker_status = await runtime.redis_manager.hgetall("worker_status")
    current_status = await runtime.get_status()
    return GenericResponse.success({
        "current_worker": current_status,
        "all_workers": {
            k: json.loads(v) for k, v in worker_status.items()
        }
    })