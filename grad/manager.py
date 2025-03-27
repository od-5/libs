"""Получение данных из системы ГРАД"""
import os
from typing import Union, List
from lib.rc_grad.api import GradAPI
from lib.rc_grad.parser import xml_to_dataclass, xml_to_dataclass_meters
from lib.rc_grad.data import Town, Street, Building, Appartment, Meter, Service


class GradManager:
    """Класс для работы с системой ГРАД"""
    _terminal_id = os.getenv('GRAD_BASE_TERMINAL_ID')

    def __init__(self, parser=xml_to_dataclass):
        self._api = GradAPI()
        self.parser = parser

    def get_town_list(
            self, owner: Union[str, None] = None, with_child: bool = False
    ) -> Union[List[Town], None]:
        """Получение списка городов"""
        resp = self._api.get_method_request(
            'get_towns', owner=owner
        )
        data = self.parser(resp, Town)
        if with_child:
            for town in data:
                child_list = self.get_street_list(town_id=town.id, with_child=True)
                if child_list is not None:
                    town.street_list = child_list
        return data

    def get_street_list(
            self, town_id: int, with_child: bool = False
    ) -> Union[List[Street], None]:
        """Получение списка улиц"""
        resp = self._api.get_method_request(
            'get_streets', town_id=town_id
        )
        data = self.parser(resp, Street)
        if with_child:
            for street in data:
                child_list = self.get_building_list(
                    town_id=town_id, street_id=street.id, with_child=True
                )
                if child_list is not None:
                    street.building_list = child_list
        return data

    def get_building_list(
            self, town_id: int, street_id: int, with_child: bool = False
    ) -> Union[List[Building], None]:
        """Получение списка зданий улицы """
        resp = self._api.get_method_request(
            'get_buildings', town_id=town_id, street_id=street_id
        )
        data = self.parser(resp, Building)
        if with_child:
            for item in data:
                child_list = self.get_appartment_list(
                    town_id=town_id, building_id=item.id
                )
                if child_list is not None:
                    item.appartment_list = child_list
        return data

    def get_appartment_list(
            self, town_id: int, building_id: int
    ) -> Union[List[Appartment], None]:
        """Получение списка квартир здания"""
        resp = self._api.get_method_request(
            'get_appartments', town_id=town_id, building_id=building_id
        )
        return self.parser(resp, Appartment)

    def get_service_list(
            self, town_id: int, abonent_id: str
    ) -> Union[List[Service], None]:
        """Получение списка оказанных услуг по помещению"""
        resp = self._api.get_method_request(
            'get_services', town_id=town_id, abonent_id=abonent_id
        )
        return self.parser(resp, Service)

    def get_meter_list(
            self, town_id: int, abonent_id: str
    ) -> Union[List[Meter], None]:
        """Получение списка приборов учёта помещения"""
        resp = self._api.get_method_request(
            'get_meters', town_id=town_id, abonent_id=abonent_id
        )
        return xml_to_dataclass_meters(resp, Meter)

    def get_full_data(self):
        """получить полную адресную базу"""
        return self.get_town_list(with_child=True)

    def set_meter_data(
            self, town_id: str, abonent_id: str, meter_id: str, meter_value: str,
            trx_id: str, terminal_id: Union[str, None] = None
    ):
        """отправка показаний ПУ"""
        terminal_id = terminal_id or self._terminal_id
        resp = self._api.get_method_request(
            'register_payments',
            town_id=town_id, abonent_id=abonent_id, meters_list=meter_id,
            charges_list=meter_value, terminal_id=terminal_id, trx_id=trx_id
        )
        return resp

    def set_payment_data(
            self, town_id: str, abonent_id: str, amount: int, datetime: int,
            trx_id: str, terminal_id: Union[str, None] = None
    ):
        """Отправка информации об оплате"""
        terminal_id = terminal_id or self._terminal_id
        resp = self._api.get_method_request(
            'register_payments',
            town_id=town_id, abonent_id=abonent_id, amount=amount, datetime=datetime,
            terminal_id=terminal_id, trx_id=trx_id
        )
        return resp
