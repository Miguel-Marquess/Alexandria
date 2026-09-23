import logging
from logtail import LogtailHandler
from alexandria.settings import Settings

settings = Settings()

logger = logging.getLogger('alexandria_info')

formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s'
)

better_stack_handler = LogtailHandler(
    source_token = settings.STACK_TOKEN,
    host=settings.STACK_HOST
)

logger.handlers = [better_stack_handler]

better_stack_handler.setLevel(logging.INFO)

logger.setLevel(logging.INFO)
