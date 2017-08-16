# TITLE_CHAR_LENGTH = 80
# COL1_LENGTH = 30
# INDENT = 3
# START_CHAR = ''
# PROPERTY_VALUE_LINE = "{:<" + str(COL1_LENGTH) + "}:{}"
# # HEADER_TEXT_FORMAT = '{:*<' + str(TITLE_CHAR_LENGTH) + '}'
# HEADER_TEXT_FORMAT = '# {}'
# TITLE_TEXT_FORMAT = '{}'
#
#
# def _decorate(decorate, value, indent=INDENT):
#     if decorate:
#         return START_CHAR + indent * ' ' + value
#     else:
#         return value
#
#
# def get_start_chars():
#     return START_CHAR + INDENT * ' '
#
#
# def create_header(text):
#     return ('', HEADER_TEXT_FORMAT.format(text.upper()), '')
#
#
# def create_title(text, decorate=True):
#     val = TITLE_TEXT_FORMAT.format(text.upper())
#     vals = (_decorate(decorate, ''),
#             _decorate(decorate, val),
#             _decorate(decorate, len(val) * '-'))
#     return vals
#
#
# def create_property(property, value, decorate=True):
#     _col = max(len(property), COL1_LENGTH)
#     _template = "{:<" + str(_col) + "}|{}"
#     val = _template.format(property, value)
#     if len(val) > TITLE_CHAR_LENGTH:
#         return (
#             _decorate(decorate, property),
#             _decorate(decorate, value)
#         )
#     return _decorate(decorate, val),
#
#
# def create_bordered(value, width=40):
#     width = max(width, len(value) + 4)
#     _empty_line = '**' + (width - 4) * ' ' + '**'
#     _txt_format = '**{:^' + str(width - 4) + '}**'
#     val = [
#         _decorate(True, width * '*'),
#         _decorate(True, _empty_line),
#         _decorate(True, _txt_format.format(value.upper())),
#         _decorate(True, _empty_line),
#         _decorate(True, width * '*')
#     ]
#     return val
#
#
# # def create_table(table_data, table_width=80, decorate=True):
# #     _len = len(table_data[0])
# #     if decorate:
# #         table_width = table_width - (len(START_CHAR) + INDENT)
# #     _col_width = int(table_width / _len)
# #     _row_format = _len * ('{:<' + str(_col_width) + '}')
# #     _vals = []
# #     for _row in table_data:
# #         _vals.append(_decorate(decorate, _row_format.format(*_row)))
# #     return _vals
#
#
# def prt(lines):
#     for _line in lines:
#         print(_line)
#
#
# if __name__ == "__main__":
#     prt(create_header("this is the start of the test"))
#     prt(create_title("title 1"))
#     prt(create_property("property 1", 123))
#     prt(create_property("property2", "abc"))
#     prt(create_title('table result'))
#     _table = [
#         ['reference', 'measurement', 'delta'],
#         [123, 3456, 34],
#         [13333, 56, 222]
#
#     ]
#     prt(create_table(_table))
#     _table1 = {
#         'data': [['ref', 'test', 'idx', 'prop', 'delta', 'pass', None, None],
#                  [0, 'count', -6, -6, 0, True, 0.0, True],
#                  [0, 'duration', 1, 1, 0, True, 0.0, True],
#                  [1, 'count', 270, 270, 0, True, 0.0, True],
#                  [1, 'duration', 21, 21, 0, True, 0.0, True]], 'pass': True}
#     prt(create_table(_table1['data']))
#     prt(create_bordered('fail'))
