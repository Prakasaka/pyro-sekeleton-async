import logging
from logging.handlers import TimedRotatingFileHandler
from pyro.utils.common import botCommon

"""
 initiate bot common init function to create necessary directories for the bot
"""

botCommon.init()

"""
 Configuration for the logger
"""

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        TimedRotatingFileHandler(botCommon.log_file, when="midnight", encoding=None,
                                 delay=False, backupCount=10),
        logging.StreamHandler()
    ]
)
logging.getLogger(__name__)


"""
 Commonly shared variables across the memory
"""
dl_object = {}
