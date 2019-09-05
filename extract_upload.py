# Extractor uploader script (Python 2.7)

#!/usr/bin/env python

import pxssh
import pexpect
import getpass
import csv


# Creating list of servers from which data will be extracted
def createServerList(serverListTextFile):
    try:
        with open(serverListTextFile, "r") as f:
            serverList = f.readlines()
        serverList = set([x.strip() for x in serverList if x])
        serverList = [x for x in serverList if x]
        return serverList
    except IOError as e:
        print str(e)

# Saving command output to a file
def uploadExtractor(hostname, ipaddress, username, password, extractorPath):
    try:
        child = pexpect.spawn('scp ' + extractorPath + ' ' + username + '@' + ipaddress + ':' + '/home/' + username + '/extract_script')
        child.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        child.sendline(password)
        child.expect([pexpect.EOF, pexpect.TIMEOUT])
        child.close()
        session = pxssh.pxssh()
        session.login(ipaddress, username, password)
        session.sendline("chmod 700 extract_script")
        session.logout()
        print (hostname + ' --- done')
    except pxssh.ExceptionPxssh as e:
        print "pxssh failed to login to " + hostname + " --- Reason: " + str(e)

# Main loop - opening csv file, calling CustomList method
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
                        uploadExtractor(hostname, ipaddress, username, password, extractorPath)
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
extractorPath = '/home/XXX/extractor_script'
serverListTxt = 'server_list.txt'
serversDataBaseCsv = 'server_database.csv'

# Beginning of a script
serverList = createServerList(serverListTxt)
password = getpass.getpass('Server(s) password:')
mainLoop(serversDataBaseCsv)
