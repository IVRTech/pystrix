import logging

class logger:
    
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
    
    def __init__(self,logger=None,debug=False,logger_name=None):
        """
        Sets up to setting AMI correct logger
        
        'logger` may be a logging.Logger object to use for logging problems in AMI threads. If not
        provided, problems will be emitted through the Python warnings interface.
        
        `debug` should only be turned on for library development.
        
        `logger_name` may be a text name to display with then logger format
        """
        
        if logger_name:
           self.NAME=logger_name
        
        if  debug :
            self._logger_level= self.DEBUG
        
        if logger and isinstance(logger, logging) :
            self._logger=logger
        else:    
            # create logger
            self._logger=logging.getLogger(self.NAME)  
            self._logger.setLevel(self._logger_level)  
            ch = logging.StreamHandler()
            ch.setLevel(self._logger_level)
            # create formatter
            formatter = logging.Formatter(self.FORMAT)
            ch.setFormatter(formatter)
            self._logger.addHandler(ch)


            
    """ Used to change the logger level
    
     `level` identifies the log level by number type
        entries.
    """
    def set_level(self, level):  
        if (level in [CRITICAL,FATAL,ERROR,WARNING,WARN,INFO,DEBUG,NOTSET] ):  
            self._logger.setLevel(level)
   
    """ Used to build tree logging 
    
    `check_level` identifies the log level to pre-check valid level
    
    """
    def _is_enable_log(self,check_level):
        setting_level= self._logger.getEffectiveLevel()
        if self._logger.isEnabledFor(check_level): # setting level
            return True
        if  check_level  > setting_level: # levels number values  10 < 20 < 30
            return True
        return False   
    
    
    """ filter logging of warning 
    
      `mesg` string with the log text to display 
    """    
    def warning(self,mesg):
        if self._is_enable_log(self.WARN):
            self._logger.warn (mesg)

    """ filter logging of debug 
        
      `mesg` string with the log text to display 
    """             
    def debug(self,mesg):
        if self._is_enable_log(self.DEBUG) and self._logger_level==self.DEBUG:
            self._logger.debug (mesg)       

    """ filter logging of error 
        
      `mesg` string with the log text to display 
    """                  
    def error(self,mesg):
        if self._is_enable_log(self.ERROR):
            self._logger.error(mesg)
            
    """ filter logging of critical 
        
      `mesg` string with the log text to display 
    """             
    def critical(self,mesg):
        if self._is_enable_log(self.CRITICAL):
            self._logger.critical (mesg)
            
    """ filter logging of info 
        
      `mesg` string with the log text to display 
    """                 
    def info(self,mesg):
        if self._is_enable_log(self.INFO):
             self._logger.info (mesg)              
             
             
    """ Display exceptions logs
         
      `mesg` string with the log text to display 
    """             
    def exception  (self,mesg):
        self._logger.exception(mesg)
                                        