"""модуль генерации контекста для SIP сервера"""
import os
from pathlib import Path


class AsteriskContext:
    """Sip context для Asterisk"""
    base_context_str = 'p-%s-ep-%s'
    base_extension_str = '[p-%s]\nexten => _Z!/%s,1,GoSub(common,s,1(${CONTEXT},${EXTEN}))'
    sip_server = os.getenv('INTERCOM_SIP_SERVER', '<some default server>')
    sip_port = os.getenv('INTERCOM_SIP_PORT', '')
    base_path = os.getenv('BASE_DIR', '/tmp/asterisk')
    dtmf_door_open = '*'

    def intercom_context(self, porch_id: int) -> str:
        """Формировние контекста для абонента Домофон"""
        return self.base_context_str % (porch_id, 0)

    def apartment_context_list(self, porch_id: int, start: int, stop: int) -> list[str]:
        """Формирование контексто для абонентов Квартир"""
        return [self.base_context_str % (porch_id, i) for i in range(start, stop+1)]

    def apartment_sip_data(self, porch_id: int, number: int):
        """sip данные для кокнретного абонента"""
        return {
            'username': self.base_context_str % (porch_id, number),
            'password': os.getenv('INTERCOM_SIP_PASSWORD', 'default_password'),
            'server': self.sip_server,
            'port': self.sip_port,
            'dtmf_door_open': self.dtmf_door_open
        }

    def extensions_dyn_str(self, porch_id_list: tuple[int]) -> str:
        """Формирование контента файла extension.dyn"""
        return '\n'.join([self.base_extension_str %
                          (i, self.intercom_context(i))
                          for i in porch_id_list])

    def pjsip_dyn_str(self, porch_list: tuple[tuple[int, ...]]) -> str:
        """Формирование контента файла pjsip.dyn"""
        def construct_pjsip_str(context):
            base_bjsip_parts = [
                '[%s](pass-auth)',
                'username=%s',
                '[%s](aor-def)',
                '[%s](p-ep)',
                'context=p-%s',
                'auth=%s',
                'aors=%s'
            ]
            for i in base_bjsip_parts:
                if i.startswith('context=p-'):
                    yield i % context.split('-')[1]
                else:
                    yield i % context
        pjsip_str = ''
        for porch in porch_list:
            p_id, p_start, p_end = porch
            pjsip_str += f';  porch id = {p_id}\n\n'
            pjsip_str += '\n'.join(
                [p_item for p_item in construct_pjsip_str(self.intercom_context(p_id))]
            )
            pjsip_str += '\n\n'
            for apartment_context in self.apartment_context_list(p_id, p_start, p_end):
                pjsip_str += '\n'.join(
                    [p_item for p_item in construct_pjsip_str(apartment_context)]
                )
                pjsip_str += '\n\n'
            pjsip_str += '\n'
        return pjsip_str

    def _generate_file(self, filename: str, content: str) -> None:
        """Запись контента в файл"""
        p = Path(self.base_path)
        p.mkdir(parents=True, exist_ok=True)
        with p.joinpath(filename) as f:
            f.write_text(content)

    def generate_extensions_file(self, porch_id_list: tuple[int, ...]) -> None:
        """Выгрузка контента в файл extensions.dyn"""
        content = self.extensions_dyn_str(porch_id_list)
        self._generate_file('extensions.dyn', content)

    def generate_pjsip_file(self, porch_list: tuple[tuple[int, int, int]]) -> None:
        """
        Выгрузка контента в файл pjsip.dyn
        """
        content = self.pjsip_dyn_str(porch_list)
        self._generate_file('pjsip.dyn', content)
