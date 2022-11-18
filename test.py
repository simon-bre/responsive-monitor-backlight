import win32gui, win32process
import time
import wmi

c = wmi.WMI()

def get_app_name(hwnd):
    """Get applicatin filename given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.Name
            break
    except:
        return None
    else:
        return exe

while(True):
    w = win32gui.GetForegroundWindow()
    print(get_app_name(w))
    #print(GetWindowText())
    time.sleep(1)