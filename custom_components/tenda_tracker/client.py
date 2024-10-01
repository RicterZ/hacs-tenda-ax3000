import logging
import codecs
import requests
import json
import os


_LOGGER = logging.getLogger(__name__)


class TendaClient:
    def __init__(self, host: str, password: str) -> None:
        self.host = host
        self.password = password
        self.cookies = None
        self.is_authorized = None

    def auth(self):
        _LOGGER.debug("Trying to authorize")
        headers = {
            'x-requested-with': 'XMLHttpRequest',
        }

        data = {
            'auth': {
                'password': codecs.encode(self.password.encode(), 'base64').decode().replace('\n', ''),
            }
        }
        response = requests.post(
            f"http://{self.host}/goform/module",
            headers=headers,
            json=data,
            verify=False,
            allow_redirects=False,
        )
        self.cookies = response.cookies

    def get_network_status(self):
        url = f'http://{self.host}/goform/module?getSystemStatus&getNetwork&getTracfficStat'
        data = {"getSystemStatus": "", "getNetwork": "", "getTracfficStat": ""}
        response = requests.post(url, json=data, cookies=self.cookies).json()
        return response

    def get_connected_devices(self):
        if self.cookies is None:
            _LOGGER.debug("Cookies not found")
            self.auth()

        response = requests.get(
            "http://" + self.host + "/goform/getOnlineList",
            verify=False,
            cookies=self.cookies,
            allow_redirects=False,
        )

        try:
            json_response = json.loads(response.content)
        except json.JSONDecodeError:
            self.cookies = None
            return self.get_connected_devices()

        devices = {}

        for device in json_response:
            mac = None
            name = None

            if "deviceId" in device:
                mac = device.get("deviceId")
            elif "localhostName" in device:
                mac = device.get("localhostMac")

            if "devName" in device:
                name = device.get("devName")
            elif "localhostName" in device:
                name = device.get("localhostName")

            if mac is not None and name is not None:
                devices[mac] = name

        return devices


if __name__ == '__main__':
    client = TendaClient('192.168.13.37', os.getenv('PASSWORD'))
    client.auth()
    print(client.get_network_status())
