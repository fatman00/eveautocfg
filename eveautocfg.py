#! /usr/bin/python

"""
bob
Use this to configure default setup on Eve-NG devices

pip freeze > requirements.txt
pip install -r requirements.txt
"""

__author__ = "Rasmus E"
__author_email__ = "fatman00hot@hotmail.com"
__copyright__ = "Copyright (c) 2020 Rasmus E"
__license__ = "MIT"

from pprint import pprint
from datetime import datetime
from argparse import ArgumentParser
import sys
import time
#import requests
import getpass
import json
import telnetlib
import csv
import re

def get_total_number(s):
    res = [i for i in s if i.isdigit()]
    return ''.join(res)

def setCDPTimers(connstring, sec):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    print(prompt.decode("ascii"))

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")
    print(prompt.decode("ascii"))

    CDPString = ("cdp timer " + sec + "\n").encode("utf-8")
    tn.write(CDPString)
    prompt = tn.read_until(b"config)#")
    print(prompt.decode("ascii"))
    tn.write(b"end\n")
    prompt = tn.read_until(b"#", 1)
    print(prompt.decode("ascii"))
    tn.close()

def delDomainLookup(connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    print(prompt.decode("ascii"))

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")
    print(prompt.decode("ascii"))

    tn.write(b"no ip domain lookup\n")
    prompt = tn.read_until(b"config)#")
    print(prompt.decode("ascii"))
    tn.write(b"end\n")
    prompt = tn.read_until(b"#", 1)
    print(prompt.decode("ascii"))
    tn.close()

def pimsmRP(connstring, rp):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    print(prompt.decode("ascii"))

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")
    print(prompt.decode("ascii"))

    RPString = ("ip pim rp-address " + rp + "\n").encode("utf-8")
    tn.write(RPString)

    tn.write(b"end\n")
    prompt = tn.read_until(b"#", 1)
    print(prompt.decode("ascii"))
    tn.close()

def setHostname(hostname, connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    print(prompt.decode("ascii"))

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")
    print(prompt.decode("ascii"))

    setHostname = ("hostname " + hostname + "\n").encode("utf-8")
    tn.write(setHostname)
    prompt = tn.read_until(b"config)#")
    print(prompt.decode("ascii"))

    tn.write(b"end\n")
    prompt = tn.read_until(b"#")
    print(prompt.decode("ascii"))

def setCdpIp(intName, connstring, prefix, lr, rr):
    sortedNum = []
    sortedNum.append(get_total_number(str(lr)).zfill(3))
    sortedNum.append(get_total_number(str(rr)).zfill(3))
    sortedNum = sorted(sortedNum)
    #print(str(sortedNum[0]))
    ipadr = ""+prefix+str(sortedNum[0])+"."+str(sortedNum[1])+"."+str(get_total_number(lr))
    mask = "255.255.255.0"
    setIntIP(intName, connstring, ipadr, mask)

def setLoIP(intName, connstring, prefix, lr):
    localNum = str(get_total_number(lr))
    #print(localNum)
    ipadr = ""+prefix+localNum+"."+localNum+"."+localNum
    mask = "255.255.255.255"
    setIntIP(intName, connstring, ipadr, mask)

def setIntIP(intName, connstring, ip, mask):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    #print(prompt.decode("ascii"))

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")
    #print(prompt.decode("ascii"))

    intString = ("int " + intName + "\n").encode("utf-8")
    tn.write(intString)
    prompt = tn.read_until(b"if)#")
    #print(prompt.decode("ascii"))
    #print(str(sortedNum[0]))
    ipString = ("ip add "+ip+" "+mask+"\n").encode("utf-8")
    tn.write(ipString)
    prompt = tn.read_until(b"if)#")
    #print(prompt.decode("ascii"))
    tn.write(b"end\n")
    prompt = tn.read_until(b"#")
    #print(prompt.decode("ascii"))

def getCDPNei(connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    print(prompt.decode("ascii"))

    tn.write(b"show cdp nei\n")
    prompt = tn.read_until(b"#")
    intArr = prompt.decode("ascii").splitlines()
    newArr = [x for x in intArr if (x.find("Eth") > 0 or x.find("Ser") > 0)]
    ints = []
    """
    nei = {
      "neiName": "R2",
      "localIF": "Eth0/0",
      "NeiIF": "Eth0/1"
    }
    """
    for int in newArr:
        nei = {}
        nei["neiName"] = int.split()[0]
        nei["localIF"] = int.split()[1]+int.split()[2]
        nei["neiIF"] = int.split()[-2] + int.split()[-1]
        ints.append(nei)
    # print(nei) #Prints int array for debug.
    return ints

def getAllInterfaces(connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    #print(prompt.decode("ascii"))

    tn.write(b"show ip int brie | inc Ether\n")
    prompt = tn.read_until(b"#\r\n", 2)
    #prompt = tn.read_all()
    intArr = prompt.decode("ascii").splitlines()
    newArr = [x for x in intArr if (x.startswith("Ether") or x.startswith("Serial"))]
    ints = []
    for int in newArr:
        ints.append(int.split()[0])
    #print(ints)

    # Running through this twice since I had some problems with buffers and stuf.
    # If you dont beleive me. just delete this code.
    tn.write(b"show ip int brie | inc Serial\n")
    prompt = tn.read_until(b"#\r\n", 2)
    # prompt = tn.read_all()
    intArr = prompt.decode("ascii").splitlines()
    newArr = [x for x in intArr if (x.startswith("Ether") or x.startswith("Serial"))]
    for int in newArr:
        ints.append(int.split()[0])
    # Delete until here.

    tn.close()
    return ints

def getAllAssInterfaces(connstring, index=0):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    #print(prompt.decode("ascii"))

    tn.write(b"show ip int brie | ex una\n")
    prompt = tn.read_until(b"#")
    intArr = prompt.decode("ascii").splitlines()
    newArr = [x for x in intArr if (x.startswith("Ether") or x.startswith("Serial") or x.startswith("Loop"))]
    ints = []
    for int in newArr:
        ints.append(int.split()[index])
    #print(ints)
    return ints

def openInterface(intName, connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")
    #print(prompt.decode("ascii"))

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")
    #print(prompt.decode("ascii"))

    intString = ("int " + intName + "\n").encode("utf-8")
    tn.write(intString)
    prompt = tn.read_until(b"if)#")
    if("Seria" in intName):
        tn.write(b"clockrate 512\n")
        prompt = tn.read_until(b"if)#")
    #print(prompt.decode("ascii"))

    tn.write(b"no shut\n")
    prompt = tn.read_until(b"if)#")
    #print(prompt.decode("ascii"))

    tn.write(b"end\n")
    prompt = tn.read_until(b"#")
    #print(prompt.decode("ascii"))

def ospfInterface(intName, connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")

    intString = ("int " + intName + "\n").encode("utf-8")
    tn.write(intString)
    prompt = tn.read_until(b"if)#")

    tn.write(b"ip ospf 1 a 0\n")
    prompt = tn.read_until(b"if)#")

    tn.write(b"end\n")
    prompt = tn.read_until(b"#")

def pimdmInterface(intName, connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")

    tn.write(b"ip multicast-routing\n")
    prompt = tn.read_until(b"config)#")

    intString = ("int " + intName + "\n").encode("utf-8")
    tn.write(intString)
    prompt = tn.read_until(b"if)#")

    tn.write(b"ip pim dense-mode\n")
    prompt = tn.read_until(b"if)#")

    tn.write(b"end\n")
    prompt = tn.read_until(b"#")

def pimsmInterface(intName, connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")

    tn.write(b"ip multicast-routing\n")
    prompt = tn.read_until(b"config)#")

    intString = ("int " + intName + "\n").encode("utf-8")
    tn.write(intString)
    prompt = tn.read_until(b"if)#")

    tn.write(b"ip pim sparse-mode\n")
    prompt = tn.read_until(b"if)#")

    tn.write(b"end\n")
    prompt = tn.read_until(b"#")

def pimsdmInterface(intName, connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")

    tn.write(b"ip multicast-routing\n")
    prompt = tn.read_until(b"config)#")

    intString = ("int " + intName + "\n").encode("utf-8")
    tn.write(intString)
    prompt = tn.read_until(b"if)#")

    tn.write(b"ip pim sparse-dense-mode\n")
    prompt = tn.read_until(b"if)#")

    tn.write(b"end\n")
    prompt = tn.read_until(b"#")

def eigrpNetwork(ipList, connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    tn.write(b"\n")
    prompt = tn.read_until(b"#")

    tn.write(b"conf t\n")
    prompt = tn.read_until(b"config)#")

    tn.write(b"router eigrp 1\n")
    prompt = tn.read_until(b"router)#")

    for ip in ipList:
        netString = ("network " + ip + " 0.0.0.0\n").encode("utf-8")
        tn.write(netString)
        prompt = tn.read_until(b"router)#")

    tn.write(b"end\n")
    prompt = tn.read_until(b"#")

def verifyPrompt(connstring):
    tn = telnetlib.Telnet(connstring.split(':')[0], connstring.split(':')[1], 10)
    while True:
        tn.write(b"\r\n")
        prompt = tn.read_until(b"#", 1)
        print("While loop prompt is: " + prompt.decode("ascii"))
        if "e initial configuration dialog? [yes/no]" in prompt.decode(("ascii")):
            tn.write(b"no\n")
        if ">" in prompt.decode(("ascii")):
            tn.write(b"en\n")
        if "#" in prompt.decode(("ascii")):
            print("Prompts is now #")
            break
        time.sleep(1)
    print("While loop prompt is: "+prompt.decode("ascii"))

if __name__ == '__main__':
    parser = ArgumentParser(description='Select options.')
    # Input parameters
    parser.add_argument('--file', type=str, default='hosts.txt',
                        help="file to parse, hostname and ip:port")
    parser.add_argument('--eveng', type=str,
                        help="IP/hostname of Eve-NG host(not implemented)")
    parser.add_argument('--username', type=str, default="admin",
                        help="username(not implemented")
    parser.add_argument('--intip', type=str, default="10.", const="10.", nargs="?",
                        help="Configure interface IPs according to hostname. Add a custom prefix. (default 10.R1.R2.R1). This will enable all interface and set cdp timer to 5 sec")
    parser.add_argument('--loopbackip', type=str, default="155.", const="155.", nargs="?",
                        help="Configure Loopback IPs according to hostname. Add a custom prefix. (default 155.R.R.R)")
    parser.add_argument('--password', type=str, default="none",
                        help="password(not implemented)")
    parser.add_argument('--hostname', action="store_true",
                        help="Configure the hostname according to hosts file")
    parser.add_argument('--ospf', action="store_true", default=True,
                        help="Configure OSPF Process 1 on all active interfaces")
    parser.add_argument('--eigrp', action="store_true", default=True,
                        help="Configure EIGRP Process 1 on all active interfaces")
    parser.add_argument('--nodomainlookup', action="store_true", default=True,
                        help="Configure no ip domain lookup")
    parser.add_argument('--pimdm', action="store_true", default=True,
                        help="Configure PIM Dense mode on all active interfaces")
    parser.add_argument('--pimsdm', action="store_true", default=True,
                        help="Configure PIM Sparce-Dense mode on all active interfaces")
    parser.add_argument('--pimsm', action="store_true", default=True,
                        help="Configure PIM Sparse mode on all active interfaces")
    parser.add_argument('--rp', type=str, default="155.1.1.1", const="155.1.1.1", nargs="?",
                        help="Configure ip pim rp-address(Default 155.1.1.1)")
    parser.add_argument('--dryrun', action="store_true",
                        help="Only do a test run without and log details without changeing configuration")
    args = parser.parse_args()
    print(sys.argv[1:])
    if args.file == None:
        print("missing filename or device")
        sys.exit(1)

    #Crap code begining right now
    if args.file is not None:
        #Loading all files in the hosts file
        with open(args.file, 'r') as f:
            reader = csv.reader(f)
            allHosts = list(reader)
        print(allHosts)
        #Set config for hosts individually

        #Enable hostprompt on all hosts
        for host in allHosts:
            verifyPrompt(host[1])

        if "--hostname" in sys.argv[1:]:
            for host in allHosts:
                setHostname(host[0], host[1])
        if "--intip" in sys.argv[1:]:
            for host in allHosts:
                setCDPTimers(host[1], "5")
                # Wait 3 seconds for the CLI to settle down.
                # To avaid the following in the middle of the show command
                # *Jan  9 08:02:38.039: %SYS-5-CONFIG_I: Configured from console by console
                interfaces = getAllInterfaces(host[1])
                # Return value: interfaces = ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', 'Ethernet0/3']
                print("Configuring NO SHUT on " + host[0] + ": " + str(interfaces))
                for int in interfaces:
                    openInterface(int, host[1])
            #All interfaces are not operational, and we need to wait for CDP to start up.
            # Min 5 sec
            print("Waiting for 6 seconds")
            time.sleep(6)
            print("Done waiting")
            #Configure IP addresses on interface in 10.HighestRouter.LowestRouter.LocalRouter. so connection between R3 end R4 will be 10.3.4.3 on R3 side and 10.3.4.4 on R4 side.
            for host in allHosts:
                CDPinterfaces = getCDPNei(host[1])
                #print(CDPinterfaces)
                print(args.intip)
                for int in CDPinterfaces:
                    print(int)
                    setCdpIp(int["localIF"], host[1], args.intip, host[0], int["neiName"])

        if "--loopbackip" in sys.argv[1:]:
            #Configure Loopback interfaces on all routers as 155.R.R.R/32
            for host in allHosts:
                setLoIP("lo0", host[1], args.loopbackip, host[0])

        if "--nodomainlookup" in sys.argv[1:]:
            #Configure Loopback interfaces on all routers as 155.R.R.R/32
            for host in allHosts:
                delDomainLookup(host[1])

        if "--rp" in sys.argv[1:]:
            #Configure RP on all routers
            for host in allHosts:
                pimsmRP(host[1], args.rp)

        if "--ospf" in sys.argv[1:]:
            for host in allHosts:
                interfaces = getAllAssInterfaces(host[1])
                # Return value: interfaces = ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', 'Ethernet0/3']
                print("Configuring OSPF on "+host[0]+": "+str(interfaces))
                for int in interfaces:
                    ospfInterface(int, host[1])
                    #print(int, host[1])

        if "--pimdm" in sys.argv[1:]:
            for host in allHosts:
                interfaces = getAllAssInterfaces(host[1])
                # Return value: interfaces = ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', 'Ethernet0/3']
                print("Configuring PIM-DM on "+host[0]+": "+str(interfaces))
                for int in interfaces:
                    pimdmInterface(int, host[1])
                    #print(int, host[1])

        if "--pimsm" in sys.argv[1:]:
            for host in allHosts:
                interfaces = getAllAssInterfaces(host[1])
                # Return value: interfaces = ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', 'Ethernet0/3']
                print("Configuring PIM-SM on "+host[0]+": "+str(interfaces))
                for int in interfaces:
                    pimsmInterface(int, host[1])
                    #print(int, host[1])

        if "--pimsdm" in sys.argv[1:]:
            for host in allHosts:
                interfaces = getAllAssInterfaces(host[1])
                # Return value: interfaces = ['Ethernet0/0', 'Ethernet0/1', 'Ethernet0/2', 'Ethernet0/3']
                print("Configuring PIM-SDM on "+host[0]+": "+str(interfaces))
                for int in interfaces:
                    pimsdmInterface(int, host[1])
                    #print(int, host[1])

        if "--eigrp" in sys.argv[1:]:
            for host in allHosts:
                interfaces = getAllAssInterfaces(host[1], 1)
                # Return value: interfaces = ['10.6.9.9', '10.8.9.9', '10.15.9.9', '155.9.9.9']
                print("Configuring EIGRP on "+host[0]+": network "+str(interfaces)+" 0.0.0.0")
                eigrpNetwork(interfaces, host[1])
