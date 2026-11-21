from collections import deque
from csv import reader, field_size_limit
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from models import PrefixStringModel
from settings import Session
from transform_symbols import symb_to_byte


field_size_limit(2147483647) # Нужно для снятия ограничения на длину считываемой за раз строки.


def read_file() -> None: # Главная функция. Вызывается в "main.py".
  normal_symbols: bool = False
    # Флаг, отвечающий за то, был ли предыдущий символ подходящим (True) или не был (False).
    # Подходящими символами являются русские буквы, а также пробел, запятая, точка, восклицательный и вопросительный знаки.
  byte_deq: deque[int] = deque() # В неё будем заносить новые подходящие символы и удалять старые (ограничение на длину - 14).
  len_deq: int = 0 # В ней будем хранить текущую длину очереди.
  barr: bytearray = bytearray(14) # Массив байтов. Нужен для переноса префиксных строк в строки для БД.
  carriage: int = 0 # Указатель на текущий символ текущей строки.
  byte: int = 0 # Переменная, хранящая текущий символ, уже преобразованный в нужный номер, а также используемая для добавления в "barr".
  cache: dict[bytes, int] = {} # Словарь для кэширования.
  k: int = 0
    # Счётчик, увеличивающийся на 1 при каждом добавлении/обновлении элемента в "cache".
    # Когда он достигает 10000 - кжш сбрасывается в БД, а сам счётчик обнуляется.
  number_row: int = 1 # Номер текущей строки csv-файла.
  with Session() as sess:
    with open(Path().cwd().parent / 'corpus.csv', 'r', encoding='utf-8') as f:
      # Файл с корпусом лежит вне папки с кодовой базой.
      # Path().cwd() возвращает папку не того файла, в котором вызывается данная функция (filling.py),
      # а файла, который является точкой входа (main.py).
      # parent возвращает родительскую папку (т.е. папку, в которой лежит папка "FillingDB").

      csv_reader = reader(f)
      next(csv_reader) # Пропустил заголовок csv-файла (т.е. корпуса).
      try: # Обернул парсинг строк из корпуса в конструкцию "try ... except" для перехвата непредвиденной ошибки и вывода номера строки, на которой произошла ошибка.
        for str in csv_reader:
          # str хранит список из 6 строк, из которых только последняя содержит полезную нагрузку
          # (т.е. только str[5] будет парситься).
          carriage = 0
          byte_deq.clear()
          len_deq = 0
          normal_symbols = False
          while carriage < len(str[5]): # Выполнять парсинг строки, пока указатель не прошёл каждый ей символ.
            byte = symb_to_byte(str[5][carriage].lower())
            if byte <= 0x20:
              normal_symbols = True
            if normal_symbols:
              if byte <= 0x25:
                byte_deq.append(byte)
                if len_deq < 14:
                  len_deq += 1
                else: byte_deq.popleft()
                for i in range(0, len_deq):
                  byte = byte_deq.pop()
                  byte_deq.appendleft(byte)
                  ind = 13 - i
                  barr[ind] = byte
                  bstr = memoryview(barr)[ind:].tobytes()
                    # Вот это сложное выражение нужно для избежания двойного копирования элементов "barr".
                  if bstr in cache:
                    cache[bstr] += 1
                  else: cache[bstr] = 1
                  k += 1
                if k >= 10000:
                  k = 0
                  values: list[dict[str, int | bytes]] = [{"pref_str": pref_str, "count": count} for pref_str, count in cache.items()]
                  stmt = insert(PrefixStringModel).values(values)
                    # Добавляет в таблицу PrefixString префиксные строки и кол-во их вхождений в корпусе.
                  
                  upsert_stmt = stmt.on_conflict_do_update(
                    index_elements=[PrefixStringModel.pref_str],
                    set_=dict(count=PrefixStringModel.count + stmt.excluded.count)
                  ) # Данный запрос делает меняет поведение запроса "stmt" таким образом:
                    # если какая-то строка уже существует в БД, то вместо добавления новой записи происходит
                    # увеличение её 2-го поля (число вхождений её префиксной строки в корпус) на число,
                    # записанное в словаре для данной строки.
                  
                  sess.execute(upsert_stmt) # Отправка запроса СУБД (т.е. выполнение запроса).
                  sess.commit() # Сохранение транзакции.
                  cache.clear()
              elif byte == 0xFF:
                normal_symbols = False
                byte_deq.clear()
                len_deq = 0
            carriage += 1
          number_row += 1
      except Exception as exc:
        print('=========================')
        print(f'number_row={number_row}')
        print('=========================')
        raise exc

    # Выполняем финальный запрос для оставшегося кэша:
    values: list[dict[str, int | bytes]] = [{"pref_str": pref_str, "count": count} for pref_str, count in cache.items()]
    stmt = insert(PrefixStringModel).values(values)
    
    upsert_stmt = stmt.on_conflict_do_update(
      index_elements=[PrefixStringModel.pref_str],
      set_=dict(count=PrefixStringModel.count + stmt.excluded.count)
    )
    
    sess.execute(upsert_stmt)
    sess.commit()
    cache.clear()
