# -*- coding: utf-8 -*-
#Author:xiaohei
#CreateTime:2014-10-25
#
# All file operations are defined here
#
#
import os
import os.path
import re
import platform
import subprocess
import inspect
import sys
import codecs
import threading
import time

curDir = os.getcwd()
bPrint = True

def list_files(src, resFiles, igoreFiles):

    if os.path.exists(src):
        if os.path.isfile(src) and src not in igoreFiles:
            resFiles.append(src)
        elif os.path.isdir(src):
            for f in os.listdir(src):
                if src not in igoreFiles:
                    list_files(os.path.join(src, f), resFiles, igoreFiles)

    return resFiles


def del_file_folder(src):
	if os.path.exists(src):
		if os.path.isfile(src):
			try:
				src = src.replace('\\', '/')
				os.remove(src)
			except:
				pass

		elif os.path.isdir(src):
			for item in os.listdir(src):
				itemsrc = os.path.join(src, item)
				del_file_folder(itemsrc)

			try:
				os.rmdir(src)
			except:
				pass


def copy_files(src, dest):
    if not os.path.exists(src):
        printF("copy files . the src is not exists.path:%s", src)
        return

    if os.path.isfile(src):
        copy_file(src, dest)
        return

    for f in os.listdir(src):
        sourcefile = os.path.join(src, f)
        targetfile = os.path.join(dest, f)
        if os.path.isfile(sourcefile):
            copy_file(sourcefile, targetfile)
        else:
            copy_files(sourcefile, targetfile)


def copy_file(src, dest):
	sourcefile = getFullPath(src)
	destfile = getFullPath(dest)
	if not os.path.exists(sourcefile):
		return
	if not os.path.exists(destfile) or os.path.getsize(destfile) != os.path.getsize(sourcefile):
		destdir = os.path.dirname(destfile)
		if not os.path.exists(destdir):
			os.makedirs(destdir)
		destfilestream = open(destfile, 'wb')
		sourcefilestream = open(sourcefile, 'rb')
		destfilestream.write(sourcefilestream.read())
		destfilestream.close()
		sourcefilestream.close()

def modifyFileContent(sourcefile, oldContent, newContent):
    if os.path.isdir(sourcefile):
        printF("The sourcefile must be a file not a dir")
        return

    if not os.path.exists(sourcefile):
        printF("The sourcefile is not exists:"+sourcefile)
        return 

    f = open(sourcefile, 'r+')
    data = str(f.read())
    f.close()
    bRet = False
    idx = data.find(oldContent)
    while idx != -1:
        data = data[:idx] + newContent + data[idx + len(oldContent):]
        idx = data.find(oldContent, idx + len(oldContent))
        bRet = True

    if bRet:
        fw = open(sourcefile, 'w')
        fw.write(data)
        fw.close()
        printF("Modify file success:"+sourcefile)
    else:
        printF("There is no content matched in file :"+sourcefile+" with content "+oldContent)


def getCurrDir():
	global curDir
	retPath = curDir
	if platform.system() == "Windows":
		retPath = retPath.decode('gbk')
	return retPath


def getFullPath(filename):
	if os.path.isabs(filename):
		return filename
	currdir = getCurrDir()
	filename = os.path.join(currdir, filename)
	filename = filename.replace('\\', '/')
	filename = re.sub('/+', '/', filename)
	return filename

def getSplashPath():
    return getFullPath("config/splash")

def getJavaBinDir():
	return getFullPath("tool/win/jre/bin/")
	#return ''

def getJavaCMD():
	return getJavaBinDir() + "java"

def getToolPath(filename):
	return "tool/win/" + filename

def getFullToolPath(filename):
    return getFullPath(getToolPath(filename))

def getFullOutputPath(appName, channel):
    path = getFullPath('output/' + appName + '/' + channel)
    #del_file_folder(path)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def execFormatCmd(cmd):
    cmd = cmd.replace('\\', '/')
    cmd = re.sub('/+', '/', cmd)
    ret = 0
    if platform.system() == 'Windows':
        st = subprocess.STARTUPINFO
        st.dwFlags = subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow = subprocess.SW_HIDE
        cmd = str(cmd).encode('gbk')
    s = subprocess.Popen(cmd, shell=True)
    ret = s.wait()
    if ret:
        s = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        #stdoutput, erroutput = s.communicate()
        #reportError(cmd, stdoutput, erroutput)
        cmd = 'ERROR:' + cmd + ' ===>>> exec Fail <<<=== '
    else:
        cmd += ' ===>>> exec success <<<=== '
    printf(cmd)
    return ret

def execWinCommand(cmd):
    os.system(cmd)  

def execWinCommandInput(tip):
    r = os.popen("set /p s=" + tip)
    txt = r.read()
    r.close()
    return txt

def printf(str):
    """
    print info in debug mode
    or
    write info into pythonLog.txt in release mode
    """
    global bPrint
    if bPrint:
        print str    

def reportError(cmd, stdoutput, erroutput):
    """
    """
    packageName = ''
    idChannel = int(threading.currentThread().getName())
    channel = ConfigParse.shareInstance().findChannel(idChannel)
    if channel != None and channel.get('packNameSuffix') != None:
        packageName = str(channel['packNameSuffix'])
        channelName = str(channel['name'])
        if platform.system() == 'Windows':
            channelName = str(channel['name']).encode('gbk')
    errorOuput = '==================>>>> ERROR <<<<==================\r\n'
    errorOuput += '[AnySDK_Channel]: ' + threading.currentThread().getName() + '\r\n'
    errorOuput += '[AnySDK_ChannelName]: ' + channelName + '\r\n'
    errorOuput += '[AnySDK_Package]: ' + packageName + '\r\n'
    errorOuput += '[AnySDK_Time]: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\r\n'
    errorOuput += '[AnySDK_Error]:\r\n'
    errorOuput += stdoutput + '\r\n'
    errorOuput += erroutput + '\r\n'
    errorOuput += '=================================================\r\n'
    log(errorOuput)


def log(str):
    outputDir = ConfigParse.shareInstance().getOutputDir()
    logDir = outputDir + '/log/'
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    logFile = codecs.open(logDir + 'error.txt', 'a+', 'utf-8')
    content = str + '\r\n'
    if platform.system() == 'Windows':
        logFile.write(unicode(content, 'gbk'))
    else:
        logFile.write(content)
    logFile.close()


def setPrintEnable(bEnable):
    global bPrint
    global curDir
    bPrint = bEnable
    curDir = sys.path[0]        


def printF(str, *params):
    str = str % (params)
    print(str)