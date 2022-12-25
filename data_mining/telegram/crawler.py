import re
from typing import List, Any

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd

from data_mining.utils.logger import LogMixin


class TGCrawler(LogMixin):
    def __init__(self, group_list: List[str]):
        self.group_list = group_list
        self.client = self.__client_reg()

    def __client_reg(self) -> TelegramClient:
        """Функция для регистрации клиента телеграмма
        Зайти на  https://my.telegram.org/  достать оттуда  App api_id,  App api_hash
        В настройке аккаунта ТГ, скопировать свой номер телефона
        Заполнить соответствующие значения"""
        API_ID: str = input("Введите API_ID:")
        API_HASH: str = input("Введите API_HASH: ")
        PHONE: str = input("Введите свой номер телефона: ")
        client = TelegramClient(PHONE, API_ID, API_HASH)
        client.start()
        return client

    def parse(self, group: str) -> List[Any]:
        """Функция для парсинга групп ТГ
        group -- ссылка на группу ТГ
        вовзвращает parser_obj в котором
        parser_obj[0] -- Pandas DataFrame
        parser_obj[1] -- Название ТГ группы"""

        def __regex_vc(txt: str) -> List[Any] or int:
            """Подфункция для фильтрации  с помощью регулярок
            На вход подается пост из группы ТГ
            Если регулярка нашла слово из regex
            Вернуть исходную строку
            Иначе вернуть 0"""
            regex_job = re.findall(
                r'\bData\b|\bMLOps\b|\bDE\b|\bDS\b|\bML\b|\bAI\b|\bNN\b|\bNLP\b|\bCV\b|\bMachine learning\b|\bData enginee\b',
                str(txt))
            if len(regex_job) != 0:
                return [txt, set(regex_job)]
            else:
                return 0

        self.logger.info(f"Канал: {group}")
        tg_group: object = self.client.get_entity(group)
        title: str = tg_group.title
        title: str = re.sub(r'[^a-z-A-Z\s\d,.]+', r'', title)
        year_list, regex_list, all_messages = [], [], []
        offset_id: int = 0
        while True:
            exit_flag: int = 0
            history = self.client(GetHistoryRequest(
                peer=tg_group,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=10000,
                max_id=0,
                min_id=0,
                hash=0
            ))
            messages: List[Any] = history.messages
            for message in messages:
                exit_flag += 1
                regex_finder_string = __regex_vc(message.message)
                if regex_finder_string != 0:
                    year_list.append(message.date.year)
                    regex_list.append(str(regex_finder_string[1]))
                    all_messages.append(message.message)
                offset_id = messages[len(messages) - 1].id
            exit_flag += 1
            if exit_flag == 1:
                df_out = pd.DataFrame({'Input_String': all_messages,
                                       'REGEX': regex_list,
                                       'year': year_list})
                self.logger.info(f"Строк для канала {group}: {len(all_messages)}")

                return [df_out, str(title)]
