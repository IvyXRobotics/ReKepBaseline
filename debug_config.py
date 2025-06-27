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
remove = {"img_base64"}

def summarize_value(value):
    """Summarize arrays and tensors, recurse through containers."""
    try:
        if isinstance(value, torch.Tensor):
            return f"<torch.Tensor shape={tuple(value.shape)} dtype={value.dtype}>"
        elif isinstance(value, np.ndarray):
            return f"<np.ndarray shape={value.shape} dtype={value.dtype}>"
        elif isinstance(value, dict):
            return {k: summarize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple, set)):
            return type(value)(summarize_value(v) for v in value)
        elif isinstance(value, (types.MethodType, types.FunctionType, types.BuiltinFunctionType)):
            return f"<function or method: {value.__name__}>"
        else:
            return value
    except Exception as e:
        return f"<Error summarizing: {e}>"

def debug_breakpoint_handler(*args, **kwargs):
    frame = inspect.currentframe().f_back
    print(f">>>>>>{frame.f_code.co_filename}({frame.f_lineno}){frame.f_code.co_name}()", file=sys.stderr)

    local_vars = frame.f_locals
    pair = (frame.f_code.co_filename, frame.f_code.co_name)

    if pair not in variable_pairs:
        variable_pairs.add(pair)

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "a") as f:
            f.write(f"\n>>>>>> {frame.f_code.co_filename}({frame.f_lineno}) in {frame.f_code.co_name}()\n")

            for name, value in local_vars.items():
                if name in remove:
                    continue

                try:
                    summarized = summarize_value(value)
                    pretty_val = pprint.pformat(summarized, depth=3, compact=True)
                except Exception as e:
                    pretty_val = f"<Error formatting {name}: {e}>"

                f.write(f"{name} = {pretty_val}\n")

    return None

os.environ["PYTHONBREAKPOINT"] = "debug_config.debug_breakpoint_handler"
