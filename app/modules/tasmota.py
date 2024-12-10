import logging
import requests

logging = logging.getLogger(__name__)

key_mapping = {
    'statuslog_seriallog': 'SerialLog',
    'statuslog_weblog': 'WebLog',
    'statuslog_syslog': 'SysLog',
    'statuslog_loghost': 'LogHost',
    'statuslog_logport': 'LogPort',
    'statuslog_teleperiod': 'TelePeriod',
}


def send_command(form_data, device_ip):
    logging.debug(form_data)
    backlog_command = "Backlog " + "%3B".join([
            f"{key_mapping.get(key, key)} {value}"
            for key, value in form_data.items()
        ])
    logging.debug(backlog_command)
    # logging.debug(form_data)
    requests.post(f"http://{device_ip}/cm?cmnd={backlog_command}")