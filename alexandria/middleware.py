from fastapi import Request, Response
from time import time
from alexandria.loggers import logger

async def log_middleware(request: Request, call_next) -> Response:
    start_time = time()

    response = await call_next(request)
    status_code = response.status_code

    response_time = time() - start_time

    log_dict = {
        "url": request.url.path,
        "method": request.method,
        "status_code": status_code,
        "response_time": response_time,
        "user_agent": request.headers.get("user-agent"),
        "client": request.client.host if request.client else None,
    }
    if status_code >= 500:
        logger.critical('HTTP Request failed', extra=log_dict)
    elif status_code >= 400:
        logger.warning('HTTP Request failed', extra=log_dict)
    else:
        logger.info('HTTP Request', extra=log_dict)

    return response
