"""

    Set of function usefull to manage folders

"""

import os
import binascii


def getAvailableFolderName(base_path, folder_name):
    """
        return a folder path that doesn't already exist by appending a unique ID after it
    """
    while True:
        random_name = str(binascii.b2a_hex(os.urandom(15)))[2:8]
        final_folder = os.path.join(base_path, folder_name + '-' + random_name)
        if not os.path.isdir(final_folder):
            break
    return final_folder