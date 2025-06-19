import os
import sys
import inspect

def debug_breakpoint_handler(*args, **kwargs):
    frame = inspect.currentframe().f_back
    print(f">>>>>>{frame.f_code.co_filename}({frame.f_lineno}){frame.f_code.co_name}()", file=sys.stderr)
    return None

os.environ["PYTHONBREAKPOINT"] = "debug_config.debug_breakpoint_handler"