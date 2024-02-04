
##########
# Logging 
##########
import logging 

FN_LOGGING = "pipeline.log"
logging.basicConfig(
    filename=FN_LOGGING,
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)



##########
# Decorators
##########

def log_func_name(func, *args, **kwargs):
    """Decorator to log.debug the function name.
    """
    @wraps(func)
    def func_name_wrap(*args, **kwargs):
        logger.debug(f"FUNC:    {func.__name__}")
        return func(*args, **kwargs)
    return func_name_wrap