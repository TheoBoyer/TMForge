"""

    Set of function usefull for value validation

"""


import os
import importlib

def assertPathExists(base_path, file=None, error_message="A file or folder wasn't found"):
    """
        Check that base_path or base_path/file if provided exist and raise a ValueError if it's not the case.
        Return the joined path
    """
    path = base_path
    if file is not None:
        path = os.path.join(base_path, file)
    if not os.path.exists(path):
        raise ValueError(error_message)
    return path

def keepPathIfExist(base_path, file=None, warning_message="A file was not found"):
    """
        Check that base_path or base_path/file if provided exist.
        Return the joined path or None if it wasn't found
    """
    path = base_path
    if file is not None:
        path = os.path.join(base_path, file)
    if not os.path.exists(path):
        print("Warning:", warning_message)
        return None
    return path

def assertFunctionExist(script_path, function_name=None):
    """
        Check that a certain function exist in a given script. Raise an error if it's not the case
        Return the actual function if it was found
    """
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

def load_config(experiment_folder):
    """
        Load the configuration file of a given experiment
    """
    experiment_folder = os.path.join(experiment_folder, "config.py")
    spec = importlib.util.spec_from_file_location("config", experiment_folder)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
