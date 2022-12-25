import re
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd

def client_reg():
    """Функция для регистрации клиента телеграмма
    Зайти на  https://my.telegram.org/  достать оттуда  App api_id,  App api_hash
    В настройке аккаунта ТГ, скопировать свой номер телефона
    Заполнить соответствующие значения"""
    print('Введите API_ID: ')
    API_ID = int(input())
    print('Введите API_HASH ')
    API_HASH = str(input())
    print('Введите свой номер телефона ')
    PHONE = str(input())
    client = TelegramClient(PHONE, API_ID, API_HASH)
    client.start()
    return client


def group_list_tg(*args):
    """Функция для создания листа из ссылок на группы телеграмма
    На вход подаются ссылки на группы телеграма
    На выходе получается лист из ссылок групп ТГ"""
    return [*args]


def tg_parser(client, adr):
    """Функция для парсинга групп ТГ
    client -- зарегистрированный клиент телеграмма
    adr -- ссылка на группу ТГ
    вовзвращает parser_obj в котором
    parser_obj[0] -- Pandas DataFrame 
    parser_obj[1] -- Название ТГ группы"""
    def _regex_vc(txt):
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

    tg_group = client.get_entity(adr)
    title = tg_group.title
    title = re.sub(r'[^a-z-A-Z\s\d,.]+', r'', title)
    year_list = []
    regex_list = []
    all_messages = []
    offset_id = 0
    while True:
        exit_flag = 0
        history = client(GetHistoryRequest(
            peer=tg_group,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=10000,
            max_id=0,
            min_id=0,
            hash=0
        ))
        messages = history.messages
        for message in messages:
            exit_flag += 1
            regex_finder_string = _regex_vc(message.message)
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

            return [df_out, str(title)]


client = client_reg()
group_list = group_list_tg('https://t.me/datasciencejobs', 'https://t.me/jobsineu', 'https://t.me/datajobschannel')

for i in group_list:
    parser_obj = tg_parser(client, i)
    df_out = parser_obj[0]
    print(len(df_out), df_out.tail(20))
    title_group = str(parser_obj[1])
    df_out.to_csv(rf"./{title_group}.csv", index=False, encoding='utf-8-sig')

