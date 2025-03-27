"""Dataclasses for RC GRAD"""
from dataclasses import dataclass, field, fields
from typing import List
from datetime import datetime


@dataclass
class BaseGrad:
    """Базовый класс"""
    id: int
    name: str

    @classmethod
    def create_from_dict(cls, dict_):
        """создать из словаря, игнорируя лишние ключи"""
        class_fields = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in dict_.items() if k in class_fields})


@dataclass
class Town(BaseGrad):
    """Города"""
    owner: str
    street_list: List['Street'] = field(default_factory=list)


@dataclass
class Street(BaseGrad):
    """Улицы"""
    building_list: List['Building'] = field(default_factory=list)


@dataclass
class Building(BaseGrad):
    """Здания"""
    owner: str
    appartment_list: List['Appartment'] = field(default_factory=list)


@dataclass
class Appartment(BaseGrad):
    """Квартиры"""
    account: str
    meter_list: List['Meter'] = field(default_factory=list)
    service_list: List['Service'] = field(default_factory=list)


@dataclass
class Service(BaseGrad):
    """Оказанные услуги"""
    saldo: int
    peni: int


@dataclass
class Meter(BaseGrad):
    """Приборы учёта"""
    service_id: int  # Код услуги с которой связан счетчик
    allowed: int  # Разрешен ли прием показаний по счетчику (1 – да, 0 – нет)
    num: str  # Заводской номер счетчика
    date: str  # дата внесения предыдущих показаний
    ind: int  # предыдущие показания, умноженные на сто
    precision: int  # Кол-во знаков ПОСЛЕ запятой при вводе показаний счетчика
    verify_date: str  # дата истечение срока гос.поверки
    status_id: int  # статус

    def _format_date(self, val):
        """Форматирование даты"""
        try:
            _date = datetime.strptime(val, '%y-%m-%d').date()
        except ValueError:
            _date = None
        return _date

    @property
    def get_date(self):
        """Дата передачи показаний"""
        return self._format_date(self.date)

    @property
    def get_verify_date(self):
        """Дата поверки"""
        return self._format_date(self.verify_date)
