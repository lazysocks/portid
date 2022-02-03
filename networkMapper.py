#!/usr/bin/env python 

from asyncore import write
from audioop import add
import subprocess as sub
import re, csv, psutil, socket, yaml
import netifaces
from sys import stdout
from pathlib import Path

def get_string(line, keyword):
    before_keyword, keyword, after_keyword = line.partition(keyword)
    str = after_keyword
    str = str.replace('\'','')
    str = str.replace(':', '')
    str = str.strip()
    return str

class settings:
    def __init__(self):
        with open('settings.yml', 'r') as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
            self.port1 = settings['known_interfaces']['port1']['mac address']


def getFields(p):
    dict = {}
    for line in p:
        #Get System Name
        if re.search(r'(System Name)', line):
            system_name = get_string(line, 'bytes')
            dict['System Name'] = system_name
               
        #Get Switch MAC
        if re.search(r'Device-ID', line):
            mac_address = get_string(line, 'bytes')
            dict['Mac Address'] = mac_address
        
        #Get IP Address
        if re.search(r'Address',line):
            ip_address = get_string(line, 'bytes')
            dict['IP Address'] = ip_address
        #Get Port ID
        if re.search(r'Port-ID', line):
            port_id = get_string(line, 'bytes')
            dict['Port ID'] = port_id
        #Get Platform
        if re.search(r'Platform', line):
            platform = get_string(line, 'bytes')
            dict['Platform'] = platform
        #Get VLAN
        if re.search(r'Native VLAN ID', line):
            vlan_id = get_string(line, 'bytes')
            dict['Native VLAN'] = vlan_id
    return dict


def getInterfaces(broadcast):
    good_interfaces = []
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        ipv4 = addrs[netifaces.AF_INET]
        for ip in ipv4:
            if broadcast in ip:
                good_interfaces.append(interface)
    return good_interfaces

def getMAC(interfaces):
    mac_addresses = []
    for interface in interfaces:
        addr = netifaces.ifaddresses(interface)
        link = addr[netifaces.AF_LINK]
        for mac in link:
            if 'addr' in mac:
                if len(mac['addr']) == 17:
                    mac_addresses.append(mac['addr'])



def write_csv(dict):
    fields = ['Port ID', 'Mac Address', 'IP Address', 'Native VLAN', 'Platform', 'System Name']

    path = Path('test.csv')
    if path.is_file():
        with open('test.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writerow(dict)
    else:
        with open('test.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerow(dict)

    
def redirect(interface):
    data = []
    
    p = sub.Popen(('sudo', 'tcpdump', '-nn', '-v', '-i',interface, '-s 1500', '-c 1', 'ether[20:2] == 0x2000' ), stdout=sub.PIPE)
    for row in iter(p.stdout.readline, b''):
        row = row.rstrip()
        row = row.decode('utf-8')
        data.append(row.strip())
    return data
     
interfaces = getInterfaces('172.16.0.255')

for interface in interfaces:
    p = redirect(interface)
    data = getFields(p)
    write_csv(data)
