#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List
from math import log2, ceil
from random import randrange


def crc32(data):
    """
    Вычисляет контрольную сумму CRC-32 для заданного сообщения.
    """
    data = data.encode('utf-8')
    crc = 0xFFFFFFFF
    poly = 0xEDB88320

    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1

    return crc ^ 0xFFFFFFFF


def __hamming_common(src: List[List[int]], s_num: int, encode=True) -> int:
    s_range = range(s_num)
    errors = 0
    for i in src:
        sindrome = 0
        for s in s_range:
            sind = 0
            for p in range(2 ** s, len(i) + 1, 2 ** (s + 1)):
                for j in range(2 ** s):
                    if (p + j) > len(i):
                        break
                    sind ^= i[p + j - 1]
            if encode:
                i[2 ** s - 1] = sind
            else:
                sindrome += (2 ** s * sind)
        if (not encode) and sindrome:
            try:
                i[sindrome - 1] = int(not i[sindrome - 1])
            except IndexError:
                errors += 1
    return errors


def hamming_encode(msg: str, mode: int = 8) -> str:
    """
    Encoding the message with Hamming code.
    :param msg: Message string to encode
    :param mode: number of significant bits
    :return:
    """

    result = ""

    msg_b = msg.encode("utf8")
    s_num = ceil(log2(log2(mode + 1) + mode + 1))  # number of control bits
    bit_seq = []
    for byte in msg_b:  # get bytes to binary values; every bits store to sublist
        bit_seq += list(map(int, f"{byte:08b}"))

    res_len = ceil((len(msg_b) * 8) / mode)  # length of result (bytes)
    bit_seq += [0] * (res_len * mode - len(bit_seq))  # filling zeros

    to_hamming = []

    for i in range(res_len):  # insert control bits into specified positions
        code = bit_seq[i * mode:i * mode + mode]
        for j in range(s_num):
            code.insert(2 ** j - 1, 0)
        to_hamming.append(code)

    errors = __hamming_common(to_hamming, s_num, True)  # process

    for i in to_hamming:
        result += "".join(map(str, i))

    return result


def hamming_decode(msg: str, mode: int = 8):
    """
    Decoding the message with Hamming code.
    :param msg: Message string to decode
    :param mode: number of significant bits
    :return:
    """

    result = ""

    s_num = ceil(log2(log2(mode + 1) + mode + 1))  # number of control bits
    res_len = len(msg) // (mode + s_num)  # length of result (bytes)
    code_len = mode + s_num  # length of one code sequence

    to_hamming = []

    for i in range(res_len):  # convert binary-like string to int-list
        code = list(map(int, msg[i * code_len:i * code_len + code_len]))
        to_hamming.append(code)

    errors = __hamming_common(to_hamming, s_num, False)  # process

    for i in to_hamming:  # delete control bits
        for j in range(s_num):
            i.pop(2 ** j - 1 - j)
        result += "".join(map(str, i))

    msg_l = []

    for i in range(len(result) // 8):  # convert from binary-sring value to integer
        val = "".join(result[i * 8:i * 8 + 8])
        msg_l.append(int(val, 2))

    # finally decode to a regular string
    try:
        result = bytes(msg_l).decode("utf-8")
    except UnicodeDecodeError:
        pass

    return result, errors


def noizer(msg: str, mode: int) -> str:
    """
    Generates an error in each element of a Hamming encoded message
    """
    seq = list(map(int, msg))
    s_num = ceil(log2(log2(mode + 1) + mode + 1))  # количество служебных битов
    code_len = mode + s_num  # длина кодового слова
    cnt = len(msg) // code_len
    result = ""

    for i in range(cnt):
        to_noize = seq[i * code_len:i * code_len + code_len]
        noize = randrange(code_len)
        to_noize[noize] = int(not to_noize[noize])
        result += "".join(map(str, to_noize))

    return result


def noizer4(msg: str, mode: int) -> str:
    """
    Generates up to 4 errors in each element of a Hamming encoded message
    """
    seq = list(map(int, msg))
    s_num = ceil(log2(log2(mode + 1) + mode + 1))  # количество служебных битов
    code_len = mode + s_num  # длина кодового слова
    cnt = len(msg) // code_len
    result = ""

    for i in range(cnt):
        to_noize = seq[i * code_len:i * code_len + code_len]
        noize1 = randrange(code_len)
        noize2 = randrange(code_len)
        noize3 = randrange(code_len)
        noize4 = randrange(code_len)
        to_noize[noize1] = int(not to_noize[noize1])
        to_noize[noize2] = int(not to_noize[noize2])
        to_noize[noize3] = int(not to_noize[noize3])
        to_noize[noize4] = int(not to_noize[noize4])
        result += "".join(map(str, to_noize))

    return result


MODE = 93  # длина слова с контрольными битами составляет 100 => значащих битов в слове 93
msg = "В 2011 году Robert C. Martin, также известный как Uncle Bob, опубликовал статью Screaming Architecture, в которой говорится, что архитектура должна «кричать» о самом приложении, а не о том, какие фреймворки в нем используются. Позже вышла статья, в которой Uncle Bob даёт отпор высказывающимся против идей чистой архитектуры. А в 2012 году он опубликовал статью «The Clean Architecture», которая и является основным описанием этого подхода. Кроме этих статей я также очень рекомендую посмотреть видео выступления Дяди Боба. Вот оригинальная схема из статьи, которая первой всплывает в голове разработчика, когда речь заходит о Clean Architecture: В Android-сообществе Clean стала быстро набирать популярность после статьи Architecting Android...The clean way?, написанной Fernando Cejas. Я впервые узнал про Clean Architecture именно из неё. И только потом пошёл искать оригинал. В этой статье Fernando приводит такую схему слоёв:\n То, что на этой схеме другие слои, а в domain слое лежат ещё какие-то Interactors и Boundaries, сбивает с толку. Оригинальная картинка тоже не всем понятна. В статьях многое неоднозначно или слегка абстрактно. А видео не все смотрят (обычно из-за недостаточного знания английского).\n И вот, из-за недопонимания, люди начинают что-то выдумывать, усложнять, заблуждаться…Давайте разбираться!\nСlean Architecture\nClean Architecture объединила в себе идеи нескольких других архитектурных подходов, которые сходятся в том, что архитектура должна:\nбыть тестируемой;\nне зависеть от UI;\nне зависеть от БД, внешних фреймворков и библиотек.\nЭто достигается разделением на слои и следованием Dependency Rule (правилу зависимостей).\nDependency Rule\nDependency Rule говорит нам, что внутренние слои не должны зависеть от внешних.\n То есть наша бизнес-логика и логика приложения не должны зависеть от презентеров, UI, баз данных и т.п. На оригинальной схеме это правило изображено стрелками, указывающими внутрь.\nВ статье сказано: имена сущностей (классов, функций, переменных, чего угодно), объявленных во внешних слоях, не должны встречаться в коде внутренних слоев.\nЭто правило позволяет строить системы, которые будет проще поддерживать, потому что изменения во внешних слоях не затронут внутренние слои.\nСлои\nUncle Bob выделяет 4 слоя:\nEntities.\n Бизнес-логика общая для многих приложений.\nUse Cases (Interactors). Логика приложения.\nInterface Adapters.\n Адаптеры между Use Cases и внешним миром. Сюда попадают Presenter’ы из MVP, а также Gateways (более популярное название репозитории). Frameworks.\n Самый внешний слой, тут лежит все остальное: UI, база данных, http-клиент, и т.п.\n"
print(f'Сообщение:\n{msg}')
checksum = crc32(msg)
print(f'Контрольная сумма: {checksum}')

# Первая отправка (без ошибок)
print('-----------ПЕРВАЯ ОТПРАВКА-----------')
enc_msg = hamming_encode(msg, MODE)
# print(f'Кодированное сообщение:\n{enc_msg}')
dec_msg, err = hamming_decode(enc_msg, MODE)
dec_msg = dec_msg[:-2:]
# print(f'Раскодированное сообщение:\n{dec_msg}')
print(f'Контрольная сумма: {crc32(dec_msg)}, корректность: {crc32(dec_msg) == checksum}')
print(f'MSG: {msg == dec_msg}')

# Вторая отправка (не более 1 ошибки на слово)
print('-----------ВТОРАЯ ОТПРАВКА-----------')
noize_msg = noizer(enc_msg, MODE)
# print(f'Кодированное сообщение с ошибками:\n{noize_msg}')
dec_msg, err = hamming_decode(noize_msg, MODE)
dec_msg = dec_msg[:-2:]
# print(f'Раскодированное сообщение:\n{dec_msg}')
print(f'Контрольная сумма: {crc32(dec_msg)}, корректность: {crc32(dec_msg) == checksum}')
print(f'MSG: {msg == dec_msg}')

# Третья отправка (4 ошибки на слово)
print('-----------ТРЕТЬЯ ОТПРАВКА-----------')
noize_msg = noizer4(enc_msg, MODE)
# print(f'Кодированное сообщение с ошибками:\n{noize_msg}')
dec_msg, err = hamming_decode(noize_msg, MODE)
dec_msg = dec_msg[:-2:]
# print(f'Раскодированное сообщение:\n{dec_msg}')
print(
    f'Контрольная сумма: {crc32(dec_msg)}, корректность: {crc32(dec_msg) == checksum}, количество обнаруженных ошибок: {err}')

