# -*- coding: utf-8 -*-
import logging
import os
import sys

from manager.config import config

_logger = logging.getLogger(__name__)
_logger_init = False
def init_logger():
    global _logger_init
    if _logger_init:
        return
    _logger_init = True

    logging.addLevelName(25, "INFO")

    # create a format for log messages and dates
    format = '%(levelname)s %(asctime)s %(pid)s %(name)s: %(message)s'
    
    # Normal Handler on stderr
    handler = logging.StreamHandler()

    if config.rc_exists and config['syslog']:
        # SysLog Handler
        if os.name == 'nt':
            handler = logging.handlers.NTEventLogHandler("%s %s" % (release.description, release.version))
        elif platform.system() == 'Darwin':
            handler = logging.handlers.SysLogHandler('/var/run/log')
        else:
            handler = logging.handlers.SysLogHandler('/dev/log')
        format = 'PiManager:%(levelname)s:%(name)s:%(message)s'

    elif config.rc_exists and config['logfile']:
        # LogFile Handler
        logf = config['logfile']
        try:
            # We check we have the right location for the log files
            dirname = os.path.dirname(logf)
            if dirname and not os.path.isdir(dirname):
                os.makedirs(dirname)
            if config['logrotate'] is not False:
                handler = logging.handlers.TimedRotatingFileHandler(filename=logf, when='D', interval=1, backupCount=30)
            elif os.name == 'posix':
                handler = logging.handlers.WatchedFileHandler(logf)
            else:
                handler = logging.FileHandler(logf)
        except Exception:
            sys.stderr.write("ERROR: couldn't create the logfile directory. Logging to the standard output.\n")

    # Check that handler.stream has a fileno() method: when running pycms
    # behind Apache with mod_wsgi, handler.stream will have type mod_wsgi.Log,
    # which has no fileno() method. (mod_wsgi.Log is what is being bound to
    # sys.stderr when the logging.StreamHandler is being constructed above.)
    def is_a_tty(stream):
        return hasattr(stream, 'fileno') and os.isatty(stream.fileno())

    if os.name == 'posix' and isinstance(handler, logging.StreamHandler) and is_a_tty(handler.stream):
        formatter = ColoredFormatter(format)
    else:
        formatter = DBFormatter(format)
        
    handler.setFormatter(formatter)

    logging.getLogger().addHandler(handler)

    # Configure loggers levels
    pseudo_config = PSEUDOCONFIG_MAPPER.get(config.rc_exists and config['log_level'] or 'info', [])

    logconfig = config.rc_exists and config['log_handler'] or []

    logging_configurations = DEFAULT_LOG_CONFIGURATION + pseudo_config + logconfig
    for logconfig_item in logging_configurations:
        loggername, level = logconfig_item.split(':')
        level = getattr(logging, level, logging.INFO)
        logger = logging.getLogger(loggername)
        logger.setLevel(level)

    for logconfig_item in logging_configurations:
        _logger.debug('logger level set: "%s"', logconfig_item)

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, _NOTHING, DEFAULT = range(10)
#The background is set with 40 plus the number of the color, and the foreground with 30
#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
COLOR_PATTERN = "%s%s%%s%s" % (COLOR_SEQ, COLOR_SEQ, RESET_SEQ)
LEVEL_COLOR_MAPPING = {
    logging.DEBUG: (BLUE, DEFAULT),
    logging.INFO: (GREEN, DEFAULT),
    logging.WARNING: (YELLOW, DEFAULT),
    logging.ERROR: (RED, DEFAULT),
    logging.CRITICAL: (WHITE, RED),
}

class DBFormatter(logging.Formatter):
    def format(self, record):
        record.pid = os.getpid()
        return logging.Formatter.format(self, record)

class ColoredFormatter(DBFormatter):
    def format(self, record):
        fg_color, bg_color = LEVEL_COLOR_MAPPING.get(record.levelno, (GREEN, DEFAULT))
        record.levelname = COLOR_PATTERN % (30 + fg_color, 40 + bg_color, record.levelname)
        return DBFormatter.format(self, record)

DEFAULT_LOG_CONFIGURATION = [
    ':INFO',
]

PSEUDOCONFIG_MAPPER = {
    'debug_rpc_answer': ['pycms:DEBUG','pycms.http.rpc.request:DEBUG', 'pycms.http.rpc.response:DEBUG'],
    'debug_rpc': ['pycms:DEBUG','pycms.http.rpc.request:DEBUG'],
    'debug': ['pycms:DEBUG'],
    'debug_sql': ['pycms.sql_db:DEBUG'],
    'info': [],
    'warn': ['pycms:WARNING', 'werkzeug:WARNING'],
    'error': ['pycms:ERROR', 'werkzeug:ERROR'],
    'critical': ['pycms:CRITICAL', 'werkzeug:CRITICAL'],
}