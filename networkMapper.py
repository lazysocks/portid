#!/usr/bin/env python 

import subprocess as sub
import re
from sys import stdout

def get_string(line, keyword):
    before_keyword, keyword, after_keyword = line.partition(keyword)
    str = after_keyword
    str = str.replace('\'','')
    str = str.replace(':', '')
    str = str.strip()


def getFields(p):
    dict = {}
    for line in p:
        #Get System Name
        if re.search(r'(System Name)', line):
            keyword =  'bytes'
            before_keyword, keyword, after_keyword = line.partition(keyword)
            system_name = after_keyword
            system_name = system_name.replace('\'','')
            system_name = system_name.replace(':','')
            dict['System Name'] = system_name
        #Get Switch MAC
        if re.search(r'(Device-ID)',line):
            keyword = ''

    
    
def redirect():
    data = []
    interface = 'ens18'
    p = sub.Popen(('sudo', 'tcpdump', '-nn', '-v', '-i', 'ens18', '-s 1500', '-c 1', 'ether[20:2] == 0x2000' ), stdout=sub.PIPE)
    for row in iter(p.stdout.readline, b''):
        row = row.rstrip()
        row = row.decode('utf-8')
        data.append(row.strip())
    return data
     

p = redirect()

getFields(p)