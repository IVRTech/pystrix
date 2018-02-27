
"""
pystrix.logger
=================================

Provides definitions and filtering rules for log event that may be raised by Pystrix 

Legal
-----

This file is part of pystrix.
pystrix is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License and
GNU Lesser General Public License along with this program. If not, see
<http://www.gnu.org/licenses/>.

(C) Ivrnet, inc., 2011

Authors:

- Miguel Arguedas

The events implemented by this module follow the definitions provided by
http://www.asteriskdocs.org/ and https://wiki.asterisk.org/
"""
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
LOGGER_NAME = 'Pystrix'   # Name to display default logger
_logger = None # instance of correct logger





""" Used to set custom logging class  """

def create(logger=None,debug=False,logger_name=None):
        """
        Sets up to setting custom logger
        
        'logger` may be a logging.Logger object to use for logging problems in AMI threads. If not
        provided, problems will be emitted through the Python warnings interface.
        
        `debug` should only be turned on for library development.
        
        `logger_name` may be a text name to display with then logger format
        """          
        if not logger_name:
            logger_name=LOGGER_NAME
        if logger and  hasattr(logger, '__class__') and  hasattr(logger.__class__, '__name__') \
         and logger.__class__.__name__ == 'Logger':
            pre_logger=logger
        else:
            if  debug :
                pre_logger= _default_logger(logger_name,DEBUG)
            else:    
                pre_logger= _default_logger(logger_name)
 
        return pre_logger
    
            
""" Used when don't exist instance of logger class 

    `name` identifies the name to show like APP Name
    `level` identifies the filter level to display messages

"""
def _default_logger(name=None,level=logging.WARNING ):
        # create logger
        _logger=logging.getLogger(name)  
        _logger.setLevel(level)  
        ch = logging.StreamHandler()
        ch.setLevel(level)
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
    if  check_level  >= setting_level: # levels number values  10 < 20 < 30
        return True
    return False   

    
""" Used to change the logger level
      
      `_logger` identifies the correct Logger to change level log
      
     `level` identifies the log level by number type
        entries.
"""
def set_level(_logger,level):  
        if (level in [CRITICAL,FATAL,ERROR,WARNING,WARN,INFO,DEBUG,NOTSET] ):  
            _logger.setLevel(level)
            

""" logging of warn 
        
   `mesg` string with the log text to display 
"""                
def warning(mesg):
    if _is_enable_log(WARN) :
         _logger.warn (mesg)
                     
warn = warning
    
"""
  logging of debug
  Limited with the params of development boolean debug  
        
 `mesg` string with the log text to display 
"""             
def debug(mesg):
    if _is_enable_log(DEBUG) and _logger.getEffectiveLevel()==DEBUG:
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
    
    
    
def _format_socket_error(exception):
    """
    Ensures that, regardless of the form that a `socket.error` takes, it is
    formatted into a readable string.
    
    @param str exception: The `socket.error` to be formatted.
    @return str: A nicely formatted summary of the exception.
    """
    try:
        (errno, message) = exception
        return "[%(errno)i] %(error)s" % {
         'errno': errno,
         'error': message,
        }
    except Exception:
        return str(exception)    
                                    