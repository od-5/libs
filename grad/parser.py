"""парсер xml -> РЦ ГРАД dataclasses"""
from xml.etree import ElementTree
from typing import Union, Type

from lib.rc_grad.data import BaseGrad, Meter


def xml_to_dataclass(xml_string: str, data_class: Type[BaseGrad]) -> Union[list[BaseGrad], None]:
    """парсер xml в datacclass or None"""
    root = ElementTree.fromstring(xml_string)
    try:
        code = int(root.find('result').find('code').text)
        result_list = root.find('result').find('list').findall('item')
    except AttributeError:
        code = 0
        result_list = False
    answer = None
    if code != 0 and result_list:
        answer = []
        for item in result_list:
            dict_item = {child.tag: child.text for child in item}
            answer.append(data_class.create_from_dict(dict_item))
    return answer


def xml_to_dataclass_meters(xml_string: str, data_class: Type[Meter]) -> Union[list[Meter], None]:
    """парсер xml в datacclass or None"""
    root = ElementTree.fromstring(xml_string)
    try:
        code = int(root.find('result').find('code').text)
        result_list = root.find('result').find('meters').findall('meter')
    except AttributeError:
        code = 0
        result_list = False
    answer = None
    if code != 0 and result_list:
        answer = []
        for item in result_list:
            answer.append(data_class.create_from_dict(item.attrib))
    return answer

