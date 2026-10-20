import ctypes
from Files.manager import manager
import threading
import time
def auto():
    global condition
    condition = True
    while condition:  # Loop runs while stop_event is not set
        manager()     # Execute manager function

def autom():
    global t1
    t1 = threading.Thread(target=auto)
    t1.start()  # Start the thread

def autom_off():
    global condition
    condition = False
    t1.join()          # Wait for the thread to finish


# Define constants
SHERB_NOCONFIRMATION = 0x00000001  # No confirmation dialog
SHERB_NOPROGRESSUI = 0x00000002    # No progress bar
SHERB_NOSOUND = 0x00000004        # No sound

# Function to check if Recycle Bin is empty
def is_recycle_bin_empty():
    try:
        # Get information about Recycle Bin
        recycle_bin_info = ctypes.wintypes.ULARGE_INTEGER()
        result = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(recycle_bin_info))
        
        if result == 0 and recycle_bin_info.QuadPart == 0:  # Check if size is 0
            return True
        return False
    except Exception as e:
        print(f"Error checking Recycle Bin: {e}")
        return False

# Function to clear Recycle Bin
def clear_recycle():
    try:
        # Check if Recycle Bin is already empty
        if is_recycle_bin_empty():
            print("Recycle Bin is already empty.")
            return

        # Call Windows API to empty Recycle Bin
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 
                                                          SHERB_NOCONFIRMATION | 
                                                          SHERB_NOPROGRESSUI | 
                                                          SHERB_NOSOUND)
        if result == 0:
            print("Recycle Bin cleared successfully.")
        else:
            print(f"Failed to clear Recycle Bin. Error code: {result}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to handle threading without blocking
def clear_recycle_bin():
    t2 = threading.Thread(target=clear_recycle)  # Create thread
    t2.start()                                  # Start thread
    
    # Non-blocking check loop
    while t2.is_alive():                         # Check if thread is still running
        time.sleep(7)                            # Wait 1 second before checking again
    
    

