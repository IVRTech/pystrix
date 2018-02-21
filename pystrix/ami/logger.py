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
    
    FORMAT = ('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    NAME = 'Pystrix'
    
    _logger = None
    _logger_level = logging.WARNING
    
    def __init__(self,logger_class=None,logger=None,debug=False):
        
        if logger_class:
           self.NAME=logger_class.__class__.__name__
        
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


            
    """ Used to change the logger level """
    def set_level(self, level):  
        if (level in [CRITICAL,FATAL,ERROR,WARNING,WARN,INFO,DEBUG,NOTSET] ):  
            self._logger.setLevel(level)
   
    """ Used to build tree logging """
    def _is_enable_log(self,check_level):
        setting_level= self._logger.getEffectiveLevel()
        if self._logger.isEnabledFor(check_level): # setting level
            return True
        if  check_level  > setting_level: # levels number values  10 < 20 < 30
            return True
        return False   
    
    
    """ filter logging of warning """    
    def warning(self,mesg):
        if self._is_enable_log(self.WARN):
            self._logger.warn (mesg)

    """ filter logging of debug """             
    def debug(self,mesg):
        if self._is_enable_log(self.DEBUG) and self._logger_level==self.DEBUG:
            self._logger.debug (mesg)       

    """ filter logging of error """                  
    def error(self,mesg):
        if self._is_enable_log(self.ERROR):
            self._logger.error(mesg)
    """ filter logging of critical """             
    def critical(self,mesg):
        if self._is_enable_log(self.CRITICAL):
            self._logger.critical (mesg)
            
    """ filter logging of info """                 
    def info(self,mesg):
        if self._is_enable_log(self.INFO):
             self._logger.info (mesg)              
             
    def exception  (self,mesg):
        self._logger.exception(mesg)
                                        