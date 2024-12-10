from database import Base 
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, func, Float, Text
from sqlalchemy.orm import relationship, load_only
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

class Devices(Base):
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String, unique=True, nullable=False)
    favorite = Column(Boolean, nullable=True)

    # Status
    status_module = Column(Integer, nullable=True)
    status_friendlyname = Column(String, nullable=True)
    status_topic = Column(String, nullable=True)
    status_buttontopic = Column(String, nullable=True)
    status_power = Column(Integer, nullable=True)
    status_poweronstate = Column(Integer, nullable=True)
    status_ledstate = Column(Integer, nullable=True)
    status_savedata = Column(Integer, nullable=True)
    status_savestate = Column(Integer, nullable=True)
    status_buttonretain = Column(Integer, nullable=True)
    status_powerretain = Column(Integer, nullable=True)

    # StatusPRM
    statusprm_baudrate = Column(Integer, nullable=True)
    statusprm_grouptopic = Column(String, nullable=True)
    statusprm_oturl = Column(String, nullable=True)
    statusprm_uptime = Column(String, nullable=True)
    statusprm_sleep = Column(Integer, nullable=True)
    statusprm_bootcount = Column(Integer, nullable=True)
    statusprm_savecount = Column(Integer, nullable=True)
    statusprm_saveaddress = Column(String, nullable=True)

    # StatusFWR
    statusfwr_version = Column(String, nullable=True)
    statusfwr_builddatetime = Column(String, nullable=True)
    statusfwr_boot = Column(Integer, nullable=True)
    statusfwr_core = Column(String, nullable=True)
    statusfwr_sdk = Column(String, nullable=True)

    # StatusLOG
    statuslog_seriallog = Column(Integer, nullable=True)
    statuslog_weblog = Column(Integer, nullable=True)
    statuslog_syslog = Column(Integer, nullable=True)
    statuslog_loghost = Column(String, nullable=True)
    statuslog_logport = Column(Integer, nullable=True)
    statuslog_ssid1 = Column(String, nullable=True)
    statuslog_ssid2 = Column(String, nullable=True)
    statuslog_teleperiod = Column(Integer, nullable=True)
    statuslog_setoption = Column(String, nullable=True)

    # StatusMEM
    statusmem_programsize = Column(Integer, nullable=True)
    statusmem_free = Column(Integer, nullable=True)
    statusmem_heap = Column(Integer, nullable=True)
    statusmem_programflashsize = Column(Integer, nullable=True)
    statusmem_flashsize = Column(Integer, nullable=True)
    statusmem_flashmode = Column(Integer, nullable=True)

    # StatusNET
    statusnet_hostname = Column(String, nullable=True)
    statusnet_ipaddress = Column(String, nullable=True)
    statusnet_gateway = Column(String, nullable=True)
    statusnet_subnetmask = Column(String, nullable=True)
    statusnet_dnssserver = Column(String, nullable=True)
    statusnet_mac = Column(String, nullable=True)
    statusnet_webserver = Column(Integer, nullable=True)
    statusnet_wificonfig = Column(Integer, nullable=True)

    # StatusTIM
    statustim_utc = Column(String, nullable=True)
    statustim_local = Column(String, nullable=True)
    statustim_startdst = Column(String, nullable=True)
    statustim_enddst = Column(String, nullable=True)
    statustim_timezone = Column(Integer, nullable=True)

    # StatusSNS
    statussns_time = Column(String, nullable=True)
    statussns_switch1 = Column(String, nullable=True)

    # StatusSTS
    statussts_time = Column(String, nullable=True)
    statussts_uptime = Column(String, nullable=True)
    statussts_vcc = Column(Float, nullable=True)
    statussts_power = Column(String, nullable=True)

    # StatusSTS - Wifi
    statussts_wifi_ap = Column(Integer, nullable=True)
    statussts_wifi_ssid = Column(String, nullable=True)
    statussts_wifi_rssi = Column(Integer, nullable=True)
    statussts_wifi_apmac = Column(String, nullable=True)

    # Method to fetch device details by ID
    @classmethod
    def get_device_by_unique_id(cls, db: Session, device_unique_id: str):
        return db.query(cls).filter(cls.unique_id == device_unique_id).first()

    # Additional method to get all devices
    @classmethod
    def get_all_devices(cls, db: Session, columns: list[str] = None):
        if columns:
            # Convert column names to ORM attributes and query explicitly
            column_attrs = [getattr(cls, column) for column in columns]
            return db.query(*column_attrs).all()
        else:
            # Default to querying the full model
            return db.query(cls).all()