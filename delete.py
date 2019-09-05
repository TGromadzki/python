# Script for deleting users from multiple Linux/AIX servers (Python 2.7)

import pxssh
import pexpect
import getpass
import csv

from collections import OrderedDict

slownik = {}
idListCsv = 'list_of_ID_to_delete.csv'
serversDataBaseCsv = 'server_database.csv'
username = 'userID'

def addToDict(key, value):
    if not slownik.has_key(key):
        slownik[key] = value
    else:
        slownik[key] += value

def createDict(idCsvFile):
    try:
        with open(idCsvFile, 'r') as csvFile:
            myCsv = csv.DictReader(csvFile)
            for iterateIdCsv in myCsv:
                if iterateIdCsv['userid'] is not "":
                    addToDict(iterateIdCsv['server'].lower(), [iterateIdCsv['userid']])
    except IOError as e:
        print str(e)

def removeDuplicatesFromDict(slownik):
    for key in slownik.iterkeys():
        slownik[key] = list(OrderedDict.fromkeys(slownik[key]))

def deleteFunc(hostname, ipaddress, systemInfo, username, password, idsTable):
    try:
        session = pxssh.pxssh()
        session.login(ipaddress, username, password)
        session.sendline('sudo su -')
        session.expect(['password :', 'Password:', pexpect.EOF, pexpect.TIMEOUT])
        session.sendline(password)
        session.expect(['#', pexpect.EOF, pexpect.TIMEOUT])
        for elem in idsTable:
            session.sendline('userdel -r ' + str(elem))
        session.sendline('exit')
        session.logout()
    except pxssh.ExceptionPxssh as e:
        print "pxssh failed to login to " + hostname + " --- Reason: " + str(e)

def mainLoop(serversDataBaseCsv, slownik):
    foundList = []
    notFoundList = []
    try:
        with open(serversDataBaseCsv, 'r') as csvFile:
            serversCsv = csv.DictReader(csvFile)
            for iterateServersCsv in serversCsv:
                for key in slownik.iterkeys():
                    if iterateServersCsv['server'].lower() == key.lower():
                        hostname = key.lower()
                        ipaddress = iterateServersCsv['ip']
                        systemInfo = iterateServersCsv['system']
                        foundList.append(str(key.lower()))
                        deleteFunc(hostname, ipaddress, systemInfo, username, password, slownik[key])
                        print str(hostname) + ' --- done'
                    else:
                        notFoundList.append(str(key.lower()))
        notFoundList = set(notFoundList)
        notFoundList = [x for x in notFoundList if x not in foundList]
        if notFoundList != []:
            print "The following servers have not been found in .csv database file: " + str(notFoundList)
    except IOError as e:
        print str(e)

password = getpass.getpass('Server(s) password:')
createDict(idListCsv)
removeDuplicatesFromDict(slownik)
mainLoop(serversDataBaseCsv, slownik)
