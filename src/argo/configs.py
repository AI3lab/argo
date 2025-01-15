import logging
from logging.handlers import RotatingFileHandler
import os
import sys

os.environ['USER_AGENT'] = 'argo'

USING_FILE_HANDLER = False

def init_logger():
    try:
        import langchain
        langchain.verbose = False
    except:
        pass

    # log format
    LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
    logger = logging.getLogger('argo')
    logger.setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.getLogger("websockets").setLevel(logging.WARNING)

    logging.getLogger("asyncio").setLevel(logging.WARNING)
    handlers = None
    if USING_FILE_HANDLER:
        # log dir
        LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

        proc_name = os.path.basename(sys.argv[0])
        proc_name = proc_name[0:-3]
        log_file = LOG_PATH + os.sep + f'{proc_name}.log'
        file_handler = RotatingFileHandler(
            filename=log_file, 
            mode='a', 
            maxBytes=(100*1024*1024),
            backupCount=10,
            encoding="utf-8",
        )
        handlers = [file_handler]

    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers,
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.INFO)

    return logger

logger = init_logger()

WS_MAX_SIZE = 1 * 1024 * 1024
LOCAL_SERVER_BASE_URL = "http://127.0.0.1:8081"

AGENT_NAME = 'argo'
COMMON_PROMPT_TEMPLATES = {
    'history':
        '<|start_header_id|>user<|end_header_id|>\n\n{question}<|eot_id|>'
        '<|start_header_id|>assistant<|end_header_id|>\n\n{answer}<|eot_id|>',
    'default_chat': 
        '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n'
        f'You are an assistant named "{AGENT_NAME}" for question-answering tasks. '
        '<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n'
        '{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>',
    'default_history_chat': 
        '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n'
        f'You are an assistant named "{AGENT_NAME}" for question-answering tasks. '
        '<|eot_id|>{history}<|start_header_id|>user<|end_header_id|>\n\n'
        '{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>',
}

WORKING_DIR = os.path.dirname(__file__)
IMAGE_DIR = os.path.join(WORKING_DIR, "images")
if not os.path.exists(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)

COMPOSITE_MODULES = {'tool', 'custom_tool'}

UPLOAD_DIR = os.path.join(WORKING_DIR, "upload")
if not os.path.exists(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

HUGGING_FACE_TOKEN = None

