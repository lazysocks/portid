#!/usr/bin/env python 

# %%
from asyncore import read, write
from audioop import add
from code import interact
import py_compile
import subprocess as sub
import re, csv, psutil, socket, yaml
import netifaces
from sys import stdout
from pathlib import Path

# %%
def get_string(line, keyword):
    before_keyword, keyword, after_keyword = line.partition(keyword)
    str = after_keyword
    str = str.replace('\'','')
    str = str.replace(':', '')
    str = str.strip()
    return str

# %%
class load_settings:
    def __init__(self):
        with open('settings.yml', 'r') as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
            self.broadcast = settings['broadcast']
            self.port1 = settings['known_interfaces']['port 1']['mac address']
            self.port2 = settings['known_interfaces']['port 2']['mac address']
            self.port3 = settings['known_interfaces']['port 3']['mac address']
            self.port4 = settings['known_interfaces']['port 4']['mac address']
            self.macs = [self.port1, self.port2, self.port3, self.port4]

        
            
            


# %%
def getFields(p, physical_port):
    dict = {}
    dict['Physical Port'] = physical_port
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
            dict['Switch Port ID'] = port_id
        #Get Platform
        if re.search(r'Platform', line):
            platform = get_string(line, 'bytes')
            dict['Platform'] = platform
        #Get VLAN
        if re.search(r'Native VLAN ID', line):
            vlan_id = get_string(line, 'bytes')
            dict['Native VLAN'] = vlan_id
    return dict

# %%
def getInterfaces(broadcast, mac_list):
    good_interfaces = []
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            ipv4 = addrs[netifaces.AF_INET]
            for ip in ipv4:
                if 'broadcast' in ip:
                    macs = addrs[netifaces.AF_LINK]
                    if broadcast in ip['broadcast']:
                        for mac in macs:
                            if 'addr' in mac and mac['addr'] in mac_list:
                                good_interfaces.append(interface)
    return good_interfaces

   
# %%
def getMAC(interface):
    addr = netifaces.ifaddresses(interface)
    link = addr[netifaces.AF_LINK]
    for address in link:
        if 'addr' in address and len(address['addr']) == 17:
            return address['addr']
# %%
def detectPort(mac, settings):
    if mac == settings.port1:
        nic = 'Port 1'
    if mac == settings.port2:
        nic = 'Port 2'
    if mac == settings.port3:
        nic = 'Port 3'
    if mac == settings.port4:
        nic = 'Port 4'
    return nic
        
           


# %%
def write_csv(dict):
    fields = ['Switch Port ID', 'Mac Address', 'IP Address', 'Native VLAN', 'Platform', 'System Name', 'Physical Port']

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

# %%    
def redirect(interface):
    data = []
    
    p = sub.Popen(('sudo', 'tcpdump', '-nn', '-v', '-i',interface, '-s 1500', '-c 1', 'ether[20:2] == 0x2000' ), stdout=sub.PIPE)
    for row in iter(p.stdout.readline, b''):
        row = row.rstrip()
        row = row.decode('utf-8')
        data.append(row.strip())
    return data

# %% 
settings = load_settings()
interfaces = getInterfaces(settings.broadcast, settings.macs)

for interface in interfaces:
    mac = getMAC(interface)
    if mac in settings.macs:
        port_num = detectPort(mac, settings)
        physical_port = input(f'Please enter the physical port attached to {port_num} with MAC {mac}: ')
        p = redirect(interface)
        data = getFields(p, physical_port)
        write_csv(data)

# %%
