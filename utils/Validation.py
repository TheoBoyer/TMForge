import os
import importlib

def assertPathExists(base_path, file=None, error_message="A file or folder wasn't found"):
    path = base_path
    if file is not None:
        path = os.path.join(base_path, file)
    if not os.path.exists(path):
        raise ValueError(error_message)
    return path

def keepPathIfExist(base_path, file=None, warning_message="A file was not found"):
    path = base_path
    if file is not None:
        path = os.path.join(base_path, file)
    if not os.path.exists(path):
        print("Warning:", warning_message)
        return None
    return path

def assertFunctionExist(script_path, function_name=None):
    spec = importlib.util.spec_from_file_location("User" + function_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if function_name is None:
        return module
    else:
        func = getattr(module, function_name, None)
        if func is None:
            raise ValueError("Unable to load {} function from {}".format(function_name, script_path))
    return func
