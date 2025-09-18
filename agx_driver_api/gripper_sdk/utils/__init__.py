from .fps import FpsCounter

from .logger_mag import LogManager, LogLevel
import logging
global_area = "DRIVER"
LogManager.init_logger(global_area=global_area, 
                    level=LogLevel.SILENT, 
                    log_to_file=False, 
                    log_file_name=None, 
                    log_file_path=None,
                    file_mode='w')
logger = LogManager.get_logger(global_area=global_area)

__all__ = [
    'FpsCounter',
    'logging',
    'LogManager',
    'LogLevel',
    'global_area',
    'logger',
]

