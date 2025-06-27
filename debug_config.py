import os
import sys
import inspect
import pprint
import types

filename = "our_code/variables.txt"

def debug_breakpoint_handler(*args, **kwargs):
    frame = inspect.currentframe().f_back
    print(f">>>>>>{frame.f_code.co_filename}({frame.f_lineno}){frame.f_code.co_name}()", file=sys.stderr)

    local_vars = frame.f_locals

    with open(filename, "a") as f:
        f.write(f"\n>>>>>> {frame.f_code.co_filename}({frame.f_lineno}) in {frame.f_code.co_name}()\n")

        for name, value in local_vars.items():
            try:
                if isinstance(value, (types.MethodType, types.FunctionType, types.BuiltinFunctionType)):
                    if hasattr(value, "shape"):
                        pretty_val = f"<array with shape {value.shape}>"
                    else:
                        pretty_val = pprint.pformat(value, depth=3, compact=True)
                else:
                    pretty_val = pprint.pformat(value, depth=3, compact=True)
            except Exception as e:
                pretty_val = f"<Error formatting {name}: {e}>"
            
            f.write(f"{name} = {pretty_val}\n")
            
    return None

os.environ["PYTHONBREAKPOINT"] = "debug_config.debug_breakpoint_handler"