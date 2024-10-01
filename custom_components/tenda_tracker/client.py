import json.decoder
import logging
import base64
import requests
import os


_LOGGER = logging.getLogger(__name__)


class TendaClient:
    _instance_map = {}

    def __init__(self, host: str, password: str) -> None:
        self.host = host
        self.password = password
        self.cookies = None
        self.is_authorized = None
        self.url = f'http://{self.host}/goform/module'

    def __new__(cls, *args, **kwargs):
        if args[0] in cls._instance_map:
            return cls._instance_map[args[0]]

        obj = object.__new__(cls)
        cls._instance_map[args[0]] = obj
        return obj

    def auth(self):
        _LOGGER.info('Trying to authorize')

        data = {'auth': {'password': base64.b64encode(self.password.encode()).decode()}}
        response = requests.post(
            self.url,
            json=data,
            verify=False,
            allow_redirects=False,
        )
        self.cookies = response.cookies
        _LOGGER.info(f'Cookie: {self.cookies}')

    def check_cookie(func: classmethod, *args, **kwargs):
        def wrap(self) -> object:
            if self.cookies is None:
                _LOGGER.info('Cookies not found')
                self.auth()
            return func(self)
        return wrap

    @check_cookie
    def get_network_status(self) -> object:
        data = {'getSystemStatus': '', 'getNetwork': '', 'getTracfficStat': ''}
        response = requests.post(self.url, json=data, cookies=self.cookies,
                                 verify=False, allow_redirects=False)
        return response.json()

    @check_cookie
    def get_connected_devices(self) -> object:
        data = {'getQosUserList': {'type': 1}}
        response = requests.post(self.url, json=data, cookies=self.cookies,
                                 verify=False, allow_redirects=False).json()

        return response['getQosUserList']


if __name__ == '__main__':
    from pprint import pprint
    client = TendaClient('192.168.13.37', os.getenv('PASSWORD'))
    pprint(client.get_network_status())
