#!/usr/bin/env python 

# %%
import subprocess as sub
import re, csv, yaml
from psutil import Popen
import netifaces
from pathlib import Path


# %%
def getInterfaces(mac_list):
    good_interfaces = []
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            ipv4 = addrs[netifaces.AF_INET]
            for ip in ipv4:
                if 'broadcast' in ip:
                    macs = addrs[netifaces.AF_LINK]
                    for mac in macs:
                        if 'addr' in mac and mac['addr'] in mac_list:
                            good_interfaces.append(interface)
    return good_interfaces

# %%
def write_csv(dict):
    fields = ['Switch Port ID', 'Mac Address', 'Switch IP Address', 'Native VLAN', 'Platform', 'System Name', 'Physical Port']

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
class load_settings:
    def __init__(self):
        with open('settings.yml', 'r') as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
            self.port1 = settings['known_interfaces']['port 1']['mac address']
            self.port2 = settings['known_interfaces']['port 2']['mac address']
            self.port3 = settings['known_interfaces']['port 3']['mac address']
            self.port4 = settings['known_interfaces']['port 4']['mac address']
            self.macs = [self.port1, self.port2, self.port3, self.port4]

# %%
class Interface:

    def __init__(self, name, settings, system_name='Unknown'):
        self.name = str(name)
        self.system_name = system_name
        self.settings = settings
        self.device_mac(self.name)
        self.detect_port()
                    
    #Get MAC address of interface
    def device_mac(self, interface):
        addr = netifaces.ifaddresses(interface)
        link = addr[netifaces.AF_LINK]
        for address in link:
            if 'addr' in address and len(address['addr']) == 17:
                self.mac = address['addr']
                
    #Get Port Number Asisgned to interface in settings file    
    def detect_port(self):
        if self.mac == self.settings.port1:
            self.nic = 'Port 1'
        if self.mac == self.settings.port2:
            self.nic = 'Port 2'
        if self.mac == self.settings.port3:
            self.nic = 'Port 3'
        if self.mac == self.settings.port4:
            self.nic = 'Port 4'

    #Prompt for physical port interface is connected to at patch panel
    def get_physical_port(self):
        self.physical_port = input(f'Please enter the physical port attached to {self.nic} with MAC {self.mac}: ') 

    def get_string(self, line):
        keyword = 'bytes'
        before_keyword, keyword, after_keyword = line.partition(keyword)
        str = after_keyword
        str = str.replace('\'','')
        str = str.replace(':', '')
        str = str.strip()
        return str

    def get_data(self, interface):
        d = []
        p = sub.Popen(('sudo', 'tcpdump', '-nn', '-v', '-i', interface, '-s 1500', '-c 1', 'ether[20:2] == 0x2000' ), stdout=sub.PIPE)
        for row in iter(p.stdout.readline, b''):
            row = row.rstrip()
            row = row.decode('utf-8')
            d.append(row.strip())
        self.data = d

    def retrieve_data(self, data):
          
        for line in data:
            #Get System Name
            if re.search(r'(System Name)', line):
                self.system_name = self.get_string(line)
            #Get Switch MAC
            if re.search(r'(Device-ID)', line):
               self.switch_mac = self.get_string(line)
            #Get IP Address
            if re.search(r'(Address)', line):
                self.ip_address = self.get_string(line)
            #Get Port ID
            if re.search(r'(Port-ID)', line):
                self.port_id = self.get_string(line)
            #Get Platform
            if re.search(r'(Platform)', line):
                self.platform = self.get_string(line)
            #Get VLAN
            if re.search(r'(Native VLAN ID)', line):
                self.vlan_id = self.get_string(line)

    def package_data(self):
        dict = {'Switch Port ID': self.port_id, 'Mac Address': self.switch_mac, 'Switch IP Address': self.ip_address,'Native VLAN': self.vlan_id, 
        'Platform': self.platform, 'System Name': self.system_name, 'Physical Port': self.physical_port}
        return dict


# %% 
def run_program():
    settings = load_settings()
    interfaces = getInterfaces(settings.macs)
    int_objs = []
    for interface in interfaces:
        int_objs.append(Interface(interface, settings))
    for int in int_objs:
        int.get_physical_port()

    for int in int_objs:
        int.get_data(int.name)
        int.retrieve_data(int.data)
        p = int.package_data()
        write_csv(p)

# %%
if __name__ == "__main__":
    run_program()