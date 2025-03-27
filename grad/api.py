"""Интерфейс API Град"""
import os
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import requests


class GradAPI:
    """Выполняет запросы к API РЦ Град"""
    _username = os.getenv('GRAD_USERNAME')
    _password = os.getenv('GRAD_PASSWORD')
    _domain = 'https://apromaco.ru:643'
    _methods = {
        'get_towns': 'lists/towns/',
        'get_streets': 'lists/streets/',
        'get_buildings': 'lists/buildings/',
        'get_appartments': 'lists/appartments/',
        'get_services': 'lists/services/',
        'get_meters': 'lists/meters/',
        'register_payments': 'register/payments/'
    }

    def __init__(self):
        self._session = self._get_session_request()

    def _get_session_request(self):
        """получение ключа сессии"""
        url_path = 'auth/'
        params = {'username': self._username, 'userpswd': self._password}
        resp = requests.get(urljoin(self._domain, url_path), params=params, timeout=30)
        root = ET.fromstring(resp.content.decode())
        try:
            session = root.find('result').find('session').text
        except AttributeError:
            session = None
        return session

    @staticmethod
    def prepare_kwargs(**kwargs):
        """преоразование параметров"""
        return {k: v for k, v in kwargs.items() if v}

    def get_method_request(self, method_name, **kwargs):
        """Выполнение запроса к api"""
        url = urljoin(self._domain, self._methods[method_name])
        params = self.prepare_kwargs(**kwargs)
        if 'session' not in params:
            params['session'] = self._session
        resp = requests.get(url, params=params, timeout=30)
        root = ET.fromstring(resp.content.decode())
        try:
            code = root.find('result').find('code').text
            desc = root.find('result').find('desc').text
        except AttributeError:
            code = '0'
            desc = 'Ошибка выполнения запроса'
        if str(code) == '0':
            if desc.lower() == 'session expired':
                self._session = self._get_session_request()
                resp = requests.get(url, params=params, timeout=30)
        return resp.content.decode()
