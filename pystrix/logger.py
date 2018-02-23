import logging


# logging level values
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
    
FORMAT = ('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Format to display default logger
NAME = 'Pystrix'   # Name to display default logger
_logger = None # instance of correct logger
_logger_level = logging.WARNING # logger display setting level activate




""" Used to set custom logging class  """
def create(logger=None,debug=False,logger_name=None):
        """
        Sets up to setting custom logger
        
        'logger` may be a logging.Logger object to use for logging problems in AMI threads. If not
        provided, problems will be emitted through the Python warnings interface.
        
        `debug` should only be turned on for library development.
        
        `logger_name` may be a text name to display with then logger format
        """
        if logger_name:
           NAME=logger_name
        
        if  debug :
            _logger_level= DEBUG
        
        if logger and isinstance(logger, logging) :
            _logger=logger


""" Used when don't exist instance of logger class """
def _default_logger():
        # create logger
        _logger=logging.getLogger(NAME)  
        _logger.setLevel(_logger_level)  
        ch = logging.StreamHandler()
        ch.setLevel(_logger_level)
        # create formatter
        formatter = logging.Formatter(FORMAT)
        ch.setFormatter(formatter)
        _logger.addHandler(ch)
        return _logger

""" Methods to use default logger without instance"""
_logger=_default_logger()
        
            
""" Used to build tree logging 
    
    `check_level` identifies the log level to pre-check valid level    
"""
def _is_enable_log(check_level):
        
    setting_level= _logger.getEffectiveLevel()
    if _logger.isEnabledFor(check_level): # setting level
        return True
    if  check_level  > setting_level: # levels number values  10 < 20 < 30
        return True
    return False   





    
""" Used to change the logger level
     `level` identifies the log level by number type
        entries.
"""
def set_level(level):  
        
        if (level in [CRITICAL,FATAL,ERROR,WARNING,WARN,INFO,DEBUG,NOTSET] ):  
            root.setLevel(level)
   
def warning(mesg):
    if _is_enable_log(WARN) :
         _logger.warn (mesg)
                     
warn = warning
    
"""
  logging of debug 
        
 `mesg` string with the log text to display 
"""             
def debug(mesg):
    if _is_enable_log(DEBUG) and _logger_level==DEBUG:
        _logger.debug (mesg)       

""" logging of error 
        
   `mesg` string with the log text to display 
"""                  
def error(mesg):
    if _is_enable_log(ERROR) :
         _logger.error(mesg)
            
""" logging of critical 
        
      `mesg` string with the log text to display 
"""             
def critical(mesg):
    if _is_enable_log(CRITICAL):
         _logger.critical (mesg)
     
fatal = critical        
""" logging of info 
        
      `mesg` string with the log text to display 
"""   
              
def info(mesg):
    if _is_enable_log(INFO):
         _logger.info (mesg)              
                    
"""  exceptions logs
         
    `mesg` string with the log text to display 
"""             
def exception(mesg):
    _logger.exception(mesg)
                                    