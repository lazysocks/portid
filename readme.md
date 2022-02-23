# networkMapper
This script will listen on any interface listed by MAC address in the settings.yml file for the Cisco Data Protocol. It will extract the Switch Port ID, MAC Address of 
connected network device, Native VLAN, Platform, and System Name.  The script will prompt for wall or patch panel port that the network cable is connected to.

## Installation
Navigate to the project directory once downloaded. Run `pipenv install` to install the necessary modules.

## Usage

Update settings.yml with MAC addresses of interfaces being used to listen for CDP packets.  Currently script supports four devices.  Run script and provide patch panel or physical port when prompted. 
```
settings.yml 
-------------
known_interfaces:
    port 1:
      mac address: '0e:a5:71:4a:f8:3f'
```


