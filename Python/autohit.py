import subprocess
import os

# adb connect localhost:21503

wd = os.getcwd()
os.chdir("C:\\adb")

p = subprocess.Popen('adb connect localhost:21503', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

for line in p.stdout.readlines():
    print (line)

retval = p.wait()

for i in range (7):
    # p = subprocess.Popen('adb shell input swipe 800 300 1000 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # retval = p.wait()
    
    # p = subprocess.Popen('adb shell input swipe 500 300 300 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # retval = p.wait()

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

    p = subprocess.Popen('adb shell input tap 200 650', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    retval = p.wait()

