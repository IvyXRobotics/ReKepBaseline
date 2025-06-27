import os
import sys
import inspect
import pprint
import types
import torch
import numpy as np
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"output_logs/variables/variable_{timestamp}.log"
variable_pairs = set()
remove = set('img_base64')

def debug_breakpoint_handler(*args, **kwargs):
    frame = inspect.currentframe().f_back
    print(f">>>>>>{frame.f_code.co_filename}({frame.f_lineno}){frame.f_code.co_name}()", file=sys.stderr)

    local_vars = frame.f_locals
    pair = tuple([frame.f_code.co_filename, frame.f_code.co_name])

    if pair not in variable_pairs:
        variable_pairs.add(pair)

        with open(filename, "a") as f:
            f.write(f"\n>>>>>> {frame.f_code.co_filename}({frame.f_lineno}) in {frame.f_code.co_name}()\n")

            for name, value in local_vars.items():
                if f"{name}" not in remove:
                    try:
                        if isinstance(value, (types.MethodType, types.FunctionType, types.BuiltinFunctionType)):
                            pretty_val = f"<function or method: {value.__name__}>"
                        elif torch is not None and isinstance(value, torch.Tensor):
                            pretty_val = f"<torch.Tensor shape={tuple(value.shape)} dtype={value.dtype}>"
                        elif np is not None and isinstance(value, np.ndarray):
                            pretty_val = f"<np.ndarray shape={value.shape} dtype={value.dtype}>"
                        else:
                            pretty_val = pprint.pformat(value, depth=3, compact=True)
                    except Exception as e:
                        pretty_val = f"<Error formatting {name}: {e}>"
                    
                    f.write(f"{name} = {pretty_val}\n")

    return None

os.environ["PYTHONBREAKPOINT"] = "debug_config.debug_breakpoint_handler"