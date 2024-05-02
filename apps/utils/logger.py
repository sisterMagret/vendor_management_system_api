import logging

logging.basicConfig(
    format="%(levelname)s %(asctime)s  %(message)s",
    level=logging.DEBUG,
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
logger = logging.getLogger(__name__)
