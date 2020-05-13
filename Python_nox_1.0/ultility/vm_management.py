import subprocess
import os
import time

import win32security
import win32api
import sys
from ntsecuritycon import *

class vm_manage:

    @staticmethod
    def check_vm_running(index):
        return
        cmd = 'memuc isvmrunning -i {}'.format(index)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        if 'Not Running' in p.stdout.read().decode():
            print("DEBUG === NOT RUNING")
            return False
        else:
            print("DEBUG === RUNING")
            return True

    @staticmethod
    def start_vm(index):
        cmd = 'memuc start -i {}'.format(index)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()


    @staticmethod
    def stop_vm(index):
        cmd = 'memuc stop -index:{}'.format(index)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    @staticmethod
    def reboot_vm(index):
        cmd = 'noxconsole reboot -index:{}'.format(index)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    @staticmethod
    def stop_app(index):
        cmd = 'memuc stopapp -i {} com.kabam.marvelbattle'.format(index)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    @staticmethod
    def start_app(index):
        cmd = 'noxconsole runapp -index:{} -packagename:com.kabam.marvelbattle'.format(index)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
    
    @staticmethod
    def open_AR(index):
        cmd = 'noxConsole runapp -index:{} -packagename:org.androidrepublic.vip'.format(index)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    @staticmethod
    def close_AR(index):
        cmd = 'noxConsole killapp -index:{} -packagename:org.androidrepublic.vip'.format(index)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    @staticmethod
    def log_vm(file, mess):
        f = open(file, 'a')
        f.write(time.asctime(time.localtime(time.time())) + ': ')
        f.write(mess + '\n')
        f.close()

    @staticmethod
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

    @staticmethod
    def RebootServer(user=None,message='Rebooting', timeout=30, bForce=0, bReboot=1):
        vm_manage.AdjustPrivilege(SE_SHUTDOWN_NAME)
        try:
            win32api.InitiateSystemShutdown(user, message, timeout, bForce, bReboot)
        finally:
            # Now we remove the privilege we just added.
            vm_manage.AdjustPrivilege(SE_SHUTDOWN_NAME, 0)

    @staticmethod
    def AbortReboot():
        vm_manage.AdjustPrivilege(SE_SHUTDOWN_NAME)
        try:
            win32api.AbortSystemShutdown(None)
        finally:
            vm_manage.AdjustPrivilege(SE_SHUTDOWN_NAME, 0)

    @staticmethod
    def reset_window():
        # Restart this PC (actual, as first parameter doesn't exist)
        vm_manage.RebootServer()

        # Restart the network PC named "Terminator" or the direct IP to restart it
        vm_manage.RebootServer("Terminator")

        # Restart this PC (actual) with all parameters :
        # User: None 
        # Message
        # Time in seconds
        # Force restart
        # restart immediately after shutting down
        # Read more about the InitiateSystemShutdown function here : https://msdn.microsoft.com/en-us/library/windows/desktop/aa376873(v=vs.85).aspx
        vm_manage.RebootServer(None,"Be careful, the computer will be restarted in 10 seconds",10,0,1)

    
    def __init__(self):
        pass
