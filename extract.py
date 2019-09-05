# Script for running specific file extractor on Linux/AIX servers and downloading the output file to local machine (Python 2.7)

#!/usr/bin/env python

import pxssh
import pexpect
import getpass
import csv
import datetime

# Creating extracted file path
def createFILEpath(hostname, dateString):
    extractedFile = "/xxx/XXX_" + str(dateString) + "_" + str(hostname.lower()) + ".extension"
    return extractedFile

# Creating list of servers from which output files will be extracted
def createServerList(serverListTextFile):
    try:
        with open(serverListTextFile, "r") as f:
            serverList = f.readlines()
        serverList = set([x.strip() for x in serverList if x])
        serverList = [x for x in serverList if x]
        return serverList
    except IOError as e:
        print str(e)

# Output file extraction
def outputFileExtract(hostname, ipaddress, username, password, destinationPath):
    try:
        session = pxssh.pxssh()
        outputFilePath = createFILEpath(hostname, dateString)
        session.login(ipaddress, username, password)
        session.sendline('sudo ./extraction_script')
        session.expect(['password :', 'Password:', pexpect.EOF, pexpect.TIMEOUT])
        session.sendline(password)
        session.expect (['Finished', pexpect.EOF, pexpect.TIMEOUT])
        session.sendline('sudo chown ' + username + ' ' + outputFilePath)
        o = session.expect(['Password:', '$', pexpect.EOF, pexpect.TIMEOUT])
        if o == 1:
            session.sendline(password)
            session.expect(['$', 'system.', pexpect.EOF, pexpect.TIMEOUT])
            session.logout()
        elif o == 2 or o == 3 or o == 4:
            session.logout()
        child = pexpect.spawn('scp ' + username + '@' + ipaddress + ':' + outputFilePath + ' ' + destinationPath)
        child.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        child.sendline(password)
        child.expect([pexpect.EOF, pexpect.TIMEOUT])
        child.close()
        print (hostname + ' --- done')
    except pxssh.ExceptionPxssh as e:
        print "pxssh failed to login to " + hostname + " --- Reason: " + str(e)

# Main loop - opening csv file, calling extract method
def mainLoop(serversDataBaseCsv):
    foundList = []
    notFoundList = []
    try:
        with open("server_database.csv", "r") as csvFile:
            myCsv = csv.DictReader(csvFile)
            for dictFromCsv in myCsv:
                for i in range(0, len(serverList)):
                    if dictFromCsv['server'].lower() == serverList[i].lower():
                        ipaddress = dictFromCsv['ip']
                        hostname = serverList[i].lower()
                        outputFileExtract(hostname, ipaddress, username, password, destinationPath)
                        foundList.append(str(serverList[i].lower()))
                    else:
                        notFoundList.append(str(serverList[i].lower()))
        notFoundList = set(notFoundList)
        notFoundList = [x for x in notFoundList if x not in foundList]
        if notFoundList != []:
            print "The following servers have not been found in .csv file: " + str(notFoundList)
    except IOError as e:
        print str(e)

# Clean variables
serverList = []
hostname = ''

# Variables
username = 'userID'
serverListTxt = 'from_which_extract.txt'
serversDataBaseCsv = 'server_list.csv'
destinationPath = '/home/XXXXX/Desktop/XXXX/'

# Beginning of a script
date = datetime.datetime.now()
dateString = str(date.strftime("%d%b%Y").upper())
serverList = createServerList(serverListTxt)
password = getpass.getpass('Server(s) password:')
mainLoop(serversDataBaseCsv)
