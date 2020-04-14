import threading
import time
import subprocess
import os

class auto_hit_class (threading.Thread):

    running = False

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    
    def run(self):
        while (self.running):
            p = subprocess.Popen('adb shell input swipe 800 300 1000 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            p = subprocess.Popen('adb shell input swipe 500 300 300 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            p = subprocess.Popen('adb shell input swipe 800 300 1000 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            p = subprocess.Popen('adb shell input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            p = subprocess.Popen('adb shell input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            p = subprocess.Popen('adb shell input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            p = subprocess.Popen('adb shell input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            p = subprocess.Popen('adb shell input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            p = subprocess.Popen('adb shell input swipe 500 300 300 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            p = subprocess.Popen('adb shell input swipe 800 300 1000 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            p = subprocess.Popen('adb shell input tap 200 650', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
        
    def start_process(self):
        self.running = True

    def stop_process(self):
        self.running = False