# Для экономии памяти на диске я решил использовать тип bytea (это массив байтов в PostgreSQL)
# для хранения префиксных строк. Но так как русские символы занимают 2 байта в UTF-8
# (а именно такая кодировка в корпусе), то мне пришлось переводить их в числа, влезающие в 1 байт.
# Для получения специального байт-номера соответствующего ему символа за O(1) использую функцию массив,
# обёрнутый в функцию с валидацией.

lst_symb_to_byte: list[int] = [0xFF] * 1106
lst_symb_to_byte[ord('\n')] = 0xFE
lst_symb_to_byte[ord('\r')] = 0xFE
lst_symb_to_byte[ord('а')] = 0x00
lst_symb_to_byte[ord('б')] = 0x01
lst_symb_to_byte[ord('в')] = 0x02
lst_symb_to_byte[ord('г')] = 0x03
lst_symb_to_byte[ord('д')] = 0x04
lst_symb_to_byte[ord('е')] = 0x05
lst_symb_to_byte[ord('ё')] = 0x06
lst_symb_to_byte[ord('ж')] = 0x07
lst_symb_to_byte[ord('з')] = 0x08
lst_symb_to_byte[ord('и')] = 0x09
lst_symb_to_byte[ord('й')] = 0x0A
lst_symb_to_byte[ord('к')] = 0x0B
lst_symb_to_byte[ord('л')] = 0x0C
lst_symb_to_byte[ord('м')] = 0x0D
lst_symb_to_byte[ord('н')] = 0x0E
lst_symb_to_byte[ord('о')] = 0x0F
lst_symb_to_byte[ord('п')] = 0x10
lst_symb_to_byte[ord('р')] = 0x11
lst_symb_to_byte[ord('с')] = 0x12
lst_symb_to_byte[ord('т')] = 0x13
lst_symb_to_byte[ord('у')] = 0x14
lst_symb_to_byte[ord('ф')] = 0x15
lst_symb_to_byte[ord('х')] = 0x16
lst_symb_to_byte[ord('ц')] = 0x17
lst_symb_to_byte[ord('ч')] = 0x18
lst_symb_to_byte[ord('ш')] = 0x19
lst_symb_to_byte[ord('щ')] = 0x1A
lst_symb_to_byte[ord('ъ')] = 0x1B
lst_symb_to_byte[ord('ы')] = 0x1C
lst_symb_to_byte[ord('ь')] = 0x1D
lst_symb_to_byte[ord('э')] = 0x1E
lst_symb_to_byte[ord('ю')] = 0x1F
lst_symb_to_byte[ord('я')] = 0x20
lst_symb_to_byte[ord(' ')] = 0x21
lst_symb_to_byte[ord(',')] = 0x22
lst_symb_to_byte[ord('.')] = 0x23
lst_symb_to_byte[ord('!')] = 0x24
lst_symb_to_byte[ord('?')] = 0x25

def symb_to_byte(symb: str) -> int:
  '''Функция, переводящая символ в номер, влезающий в 1 байт. 
  Символы сброса каретки и перехода на следующую строку отображаются в 0xFE, 
  остальные неподходящие символы - в 0xFF.'''
  if len(symb) > 1: return 0xFF
  ord_symb = ord(symb)
  if ord_symb >= 1106: return 0xFF
  return lst_symb_to_byte[ord_symb]


# lst_byte_to_symb: list[str] = [''] * 38
# lst_byte_to_symb[0] = 'а'
# lst_byte_to_symb[1] = 'б'
# lst_byte_to_symb[2] = 'в'
# lst_byte_to_symb[3] = 'г'
# lst_byte_to_symb[4] = 'д'
# lst_byte_to_symb[5] = 'е'
# lst_byte_to_symb[6] = 'ё'
# lst_byte_to_symb[7] = 'ж'
# lst_byte_to_symb[8] = 'з'
# lst_byte_to_symb[9] = 'и'
# lst_byte_to_symb[10] = 'й'
# lst_byte_to_symb[11] = 'к'
# lst_byte_to_symb[12] = 'л'
# lst_byte_to_symb[13] = 'м'
# lst_byte_to_symb[14] = 'н'
# lst_byte_to_symb[15] = 'о'
# lst_byte_to_symb[16] = 'п'
# lst_byte_to_symb[17] = 'р'
# lst_byte_to_symb[18] = 'с'
# lst_byte_to_symb[19] = 'т'
# lst_byte_to_symb[20] = 'у'
# lst_byte_to_symb[21] = 'ф'
# lst_byte_to_symb[22] = 'х'
# lst_byte_to_symb[23] = 'ц'
# lst_byte_to_symb[24] = 'ч'
# lst_byte_to_symb[25] = 'ш'
# lst_byte_to_symb[26] = 'щ'
# lst_byte_to_symb[27] = 'ъ'
# lst_byte_to_symb[28] = 'ы'
# lst_byte_to_symb[29] = 'ь'
# lst_byte_to_symb[30] = 'э'
# lst_byte_to_symb[31] = 'ю'
# lst_byte_to_symb[32] = 'я'
# lst_byte_to_symb[33] = ' '
# lst_byte_to_symb[34] = ','
# lst_byte_to_symb[35] = '.'
# lst_byte_to_symb[36] = '!'
# lst_byte_to_symb[37] = '?'

# def byte_to_symb(arg: bytes) -> str:
#   return lst_byte_to_symb[arg[0]]

# def bytes_to_str(arg: bytes) -> str:
#   result = ''
#   for b in arg:
#     result = result + (lst_byte_to_symb[b])
#   return result

# def str_to_bytes(arg: str) -> bytes:
#   barr = bytearray(len(arg))
#   for i in range(len(arg)):
#     barr[i] = symb_to_byte(arg[i])
#   return memoryview(barr).tobytes()
