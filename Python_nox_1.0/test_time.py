import win32security
import win32api
import sys
import time
from ntsecuritycon import *

def AdjustPrivilege(priv, enable=1):
    # Get the process token
    flags = TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY
    htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
    # Get the ID for the system shutdown privilege.
    idd = win32security.LookupPrivilegeValue(None, priv)
    # Now obtain the privilege for this process.
    # Create a list of the privileges to be added.
    if enable:
        newPrivileges = [(idd, SE_PRIVILEGE_ENABLED)]
    else:
        newPrivileges = [(idd, 0)]
    # and make the adjustment
    win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)

def RebootServer(user=None,message='Rebooting', timeout=30, bForce=0, bReboot=1):
    AdjustPrivilege(SE_SHUTDOWN_NAME)
    try:
        win32api.InitiateSystemShutdown(user, message, timeout, bForce, bReboot)
    finally:
        # Now we remove the privilege we just added.
        AdjustPrivilege(SE_SHUTDOWN_NAME, 0)

def AbortReboot():
    AdjustPrivilege(SE_SHUTDOWN_NAME)
    try:
        win32api.AbortSystemShutdown(None)
    finally:
        AdjustPrivilege(SE_SHUTDOWN_NAME, 0)

start = time.time()

time.sleep(1)

end = time.time()

print(time.asctime( time.localtime(time.time())))

print(end - start)

# Restart this PC (actual, as first parameter doesn't exist)
RebootServer()

# Restart the network PC named "Terminator" or the direct IP to restart it
RebootServer("Terminator")

# Restart this PC (actual) with all parameters :
# User: None 
# Message
# Time in seconds
# Force restart
# restart immediately after shutting down
# Read more about the InitiateSystemShutdown function here : https://msdn.microsoft.com/en-us/library/windows/desktop/aa376873(v=vs.85).aspx
RebootServer(None,"Be careful, the computer will be restarted in 30 seconds",30,0,1)