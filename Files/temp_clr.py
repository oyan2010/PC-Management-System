import os
import shutil
def clear_temp():
    folder_path = os.path.expanduser('~\\AppData\\Local\\Temp')
    folder_data = os.listdir(folder_path)
    for item in folder_data:
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            return f'Error Occurs, Reason: {e}'



