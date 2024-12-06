from sqlalchemy import create_engine, Column, String, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.devices import Devices
from sqlalchemy.orm import Session
import json
import requests
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import socket
import logging
import secrets

logging = logging.getLogger(__name__)

def ping_device(ip):
    """
    Pings an IP address to check if it's reachable.

    Args:
        ip (str): The IP address to ping.

    Returns:
        bool: True if reachable, False otherwise.
    """
    try:
        response = requests.get(f"http://{ip}/cm?cmnd=Status", timeout=1)
        if response.status_code == 200:
            return response.json()  # Assume JSON response for Tasmota devices
    except requests.RequestException:
        pass
    return None

def get_device_status(ip):
    """Send HTTP request to Tasmota device to retrieve its status."""
    url = f"http://{ip}/cm?cmnd=Status%200"  # Query for StatusNET (device network info)
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()
    
    except requests.RequestException as e:
        # Handle connection errors or timeouts
        print(f"Error querying {ip}: {e}")
        return None
    
def update_device_from_status(device_data, device):
    """
    Update the device model instance with the data from the Tasmota response.
    """
    # Update Status section
    status = device_data.get("Status", {})
    device.status_module = status.get("Module")
    device.status_friendlyname = status.get("FriendlyName")
    device.status_topic = status.get("Topic")
    device.status_buttontopic = status.get("ButtonTopic")
    device.status_power = status.get("Power")
    device.status_poweronstate = status.get("PowerOnState")
    device.status_ledstate = status.get("LedState")
    device.status_savedata = status.get("SaveData")
    device.status_savestate = status.get("SaveState")
    device.status_buttonretain = status.get("ButtonRetain")
    device.status_powerretain = status.get("PowerRetain")

    # Update StatusPRM section
    statusprm = device_data.get("StatusPRM", {})
    device.statusprm_baudrate = statusprm.get("Baudrate")
    device.statusprm_grouptopic = statusprm.get("GroupTopic")
    device.statusprm_oturl = statusprm.get("OtaUrl")
    device.statusprm_uptime = statusprm.get("Uptime")
    device.statusprm_sleep = statusprm.get("Sleep")
    device.statusprm_bootcount = statusprm.get("BootCount")
    device.statusprm_savecount = statusprm.get("SaveCount")
    device.statusprm_saveaddress = statusprm.get("SaveAddress")

    # Update StatusFWR section
    statusfwr = device_data.get("StatusFWR", {})
    device.statusfwr_version = statusfwr.get("Version")
    device.statusfwr_builddatetime = statusfwr.get("BuildDateTime")
    device.statusfwr_boot = statusfwr.get("Boot")
    device.statusfwr_core = statusfwr.get("Core")
    device.statusfwr_sdk = statusfwr.get("SDK")

    # Update StatusLOG section
    statuslog = device_data.get("StatusLOG", {})
    device.statuslog_seriallog = statuslog.get("SerialLog")
    device.statuslog_weblog = statuslog.get("WebLog")
    device.statuslog_syslog = statuslog.get("SysLog")
    device.statuslog_loghost = statuslog.get("LogHost")
    device.statuslog_logport = statuslog.get("LogPort")
    device.statuslog_ssid1 = statuslog.get("SSId1")
    device.statuslog_ssid2 = statuslog.get("SSId2")
    device.statuslog_teleperiod = statuslog.get("TelePeriod")
    device.statuslog_setoption = statuslog.get("SetOption")

    # Update StatusMEM section
    statusmem = device_data.get("StatusMEM", {})
    device.statusmem_programsize = statusmem.get("ProgramSize")
    device.statusmem_free = statusmem.get("Free")
    device.statusmem_heap = statusmem.get("Heap")
    device.statusmem_programflashsize = statusmem.get("ProgramFlashSize")
    device.statusmem_flashsize = statusmem.get("FlashSize")
    device.statusmem_flashmode = statusmem.get("FlashMode")

    # Update StatusNET section
    statusnet = device_data.get("StatusNET", {})
    device.statusnet_hostname = statusnet.get("Hostname")
    device.statusnet_ipaddress = statusnet.get("IPAddress")
    device.statusnet_gateway = statusnet.get("Gateway")
    device.statusnet_subnetmask = statusnet.get("Subnetmask")
    device.statusnet_dnssserver = statusnet.get("DNSServer")
    device.statusnet_mac = statusnet.get("Mac")
    device.statusnet_webserver = statusnet.get("Webserver")
    device.statusnet_wificonfig = statusnet.get("WifiConfig")

    # Update StatusTIM section
    statustim = device_data.get("StatusTIM", {})
    device.statustim_utc = statustim.get("UTC")
    device.statustim_local = statustim.get("Local")
    device.statustim_startdst = statustim.get("StartDST")
    device.statustim_enddst = statustim.get("EndDST")
    device.statustim_timezone = statustim.get("Timezone")

    # Update StatusSNS section
    statussns = device_data.get("StatusSNS", {})
    device.statussns_time = statussns.get("Time")
    device.statussns_switch1 = statussns.get("Switch1")

    # Update StatusSTS section
    statussts = device_data.get("StatusSTS", {})
    device.statussts_time = statussts.get("Time")
    device.statussts_uptime = statussts.get("Uptime")
    device.statussts_vcc = statussts.get("Vcc")
    device.statussts_power = statussts.get("POWER")

    # Update StatusSTS - Wifi section
    wifi = statussts.get("Wifi", {})
    device.statussts_wifi_ap = wifi.get("AP")
    device.statussts_wifi_ssid = wifi.get("SSId")
    device.statussts_wifi_rssi = wifi.get("RSSI")
    device.statussts_wifi_apmac = wifi.get("APMac")

    # format specific fields to fit DB
    device.status_friendlyname = json.dumps(device.status_friendlyname)
    device.statuslog_setoption = json.dumps(device.statuslog_setoption)

def discover(ip_start, ip_end, db: Session):

    errors = []
    devices_new = 0
    devices_updated = 0
    
    try:
        ip_start = ipaddress.IPv4Address(ip_start)
    except Exception as e:
        # errors['ip_start'] = {"title": "Validation failed for starting IP", "message": e}
        errors.append({"title": "Validation failed for starting IP", "message": e})
    
    try:
        ip_end = ipaddress.IPv4Address(ip_end)
    except Exception as e:
        # errors['ip_end'] = {"title": "Validation failed for ending IP", "message": e}
        errors.append({"title": "Validation failed for ending IP", "message": e})
    
    if errors:
        return {"errors": errors}
    
    subnets = ipaddress.summarize_address_range(ip_start, ip_end)
    for subnet in subnets:
        logging.debug("Checking subnet: '%s'", str(subnet))
        reachable_devices = []
        ip_list = [str(ip) for ip in ipaddress.ip_network(subnet, strict=False)]

        # Perform multithreaded pinging and device querying
        with ThreadPoolExecutor() as executor:
            ping_results = list(executor.map(ping_device, ip_list))  # Ping devices first

        # After pinging, query only the devices that are reachable
        reachable_ips = [ip for ip, is_reachable in zip(ip_list, ping_results) if is_reachable]

        # Now query only the reachable devices
        with ThreadPoolExecutor() as executor:
            results = executor.map(get_device_status, reachable_ips)

        # Collect reachable Tasmota devices
        for ip, result in zip(reachable_ips, results):
            if result:
                logging.info(f"Tasmota device found at {ip}: {result}")
                reachable_devices.append({"ip": ip, "details": result})

                mac_address = result.get("StatusNET", {}).get("Mac", "")
                if mac_address:
                    # Check if the device already exists in the database
                    existing_device = db.query(Devices).filter(Devices.statusnet_mac == mac_address).first()

                    if existing_device:
                        # Update the existing device
                        logging.info(f"Updating device with MAC address {mac_address}")
                        update_device_from_status(result, existing_device)
                        db.commit()
                        devices_updated += 1
                    else:
                        # Add new device if it doesn't exist
                        new_device = Devices(statusnet_mac=mac_address)
                        update_device_from_status(result, new_device)
                        new_device.ip_address = ip  # Set additional fields
                        new_device.unique_id = secrets.token_hex(16)
                        db.add(new_device)
                        db.commit()
                        devices_new += 1

    devices = {"new": devices_new, "updated": devices_updated}

    return { "devices": devices, "errors": errors }

