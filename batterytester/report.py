import datetime
import os

from batterytester.helpers import check_output_location

SUMMARY_FILE_FORMAT = 'summary-report.md'

# from batterytester.reporter import create_property
import time

H2_FORMAT = '## {}'
ITALIC_FORMAT = '*{}*'
BOLD_FORMAT = '**{}**'
DL_VALUE_FORMAT = ':   {}'
BLOCKQUOTE_FORMAT = '> {}'

COL1_WIDTH = 30
TEXT_WIDTH = 80


def header(content, level):
    return ('#' * level) + ' ' + content


def italic(content):
    return ITALIC_FORMAT.format(content)


def bold(content):
    return BOLD_FORMAT.format(content)


def block_quote(content):
    return BLOCKQUOTE_FORMAT.format(content)


class Report:
    def __init__(self, output_path):
        self.summary = []
        self._filename = None
        self._output_path= output_path
        self.define_filename()
        self.create_summary_file()

    def define_filename(self):
        self._filename = os.path.join(self._output_path, SUMMARY_FILE_FORMAT)

    def create_summary_file(self):
        with open(self._filename,'w') as fl:
            fl.write('TEST SUMMARY FILE.\n\n')


    def p(self, content):
        self._output(((content), ''))

    def H1(self, content):
        self._output((header(content, 1), ''))

    def H2(self, content):
        self._output((H2_FORMAT.format(content), ''))

    def line(self, char='-'):
        self._output(char * TEXT_WIDTH)

    def italic(self, content):
        self._output(italic(content))

    def bold(self, content):
        self._output(bold(content))

    def create_bordered(self, content):
        self.line()
        self.italic(content)
        self.line()

    def create_dl(self, property, value):
        self._output(property)
        self._output(DL_VALUE_FORMAT.format(value))

    def final_test_result(self, success: bool, reason):
        self.test_result(success)
        self._output(block_quote(reason))

    def test_result(self, success: bool):
        result = 'PASS'
        if not success:
            result = 'FAIL'
        _content = bold(result)
        _content = header(_content, 2)
        self._output(block_quote(_content))

    def create_property_table(self, *rows):
        """Creates a table of key value pairs."""
        header = ('property', 'value')
        self.create_table(header, *rows)

    def create_table(self, header, *rows):
        _colwidths = []

        def add_col_width(value, idx):
            try:
                _old_val = _colwidths[idx]
                if value > _old_val:
                    _colwidths[idx] = value
            except IndexError:
                if idx == 0:
                    value = max(value, COL1_WIDTH)
                _colwidths.append(value)

        for idx, _col in enumerate(header):
            add_col_width(len(_col), idx)
        for _row in rows:
            for idx, _col in enumerate(_row):
                add_col_width(len(str(_col)), idx)

        output = []
        output.append(' | '.join(
            (value.ljust(width) for value, width in zip(header, _colwidths))))
        output.append(' | '.join('-' * width for width in _colwidths))

        for _row in rows:
            output.append(
                ' | '.join(
                    (str(value).ljust(width) for value, width in
                     zip(_row, _colwidths))
                )
            )
        # add an empty line to the end.
        output.append('')
        self._output(output)

        # def create_property(self, property, value):
        #     self.create_dl(property, value)
        # self._output(create_property(property, value))

    def _output(self, output):
        if isinstance(output, str):
            print(output)
            self.summary.append(output)
        else:
            for _o in output:
                print(_o)
            self.summary.extend(output)

    def write_summary_to_file(self):
        if os.path.exists(self._filename):
            _mode = 'a'
        else:
            _mode='w'
        with open(self._filename, _mode) as fl:
            fl.write('\n'.join(self.summary))
        # reset the summary
        self.summary = []

    def report_timing(self, start, stop):
        _header = ('started', 'stopped', 'duration[seconds]')
        _row = (str(start), str(stop), str((stop - start).total_seconds()))
        self.create_table(_header, _row)

    def write_intro(self, test_name):
        self.H1("TEST : {}".format(test_name))
        # self.p('started: {}'.format(str(get)))
        # self._output(
        #     create_property('test name', test_name)
        # )
        # self._output(
        #     create_property('creation date', str(datetime.datetime.now())))


if __name__ == "__main__":
    rep = Report('test')
    mode = 'learning mode'
    current_loop = 5
    idx = 1
    rep.test_result(True)
    rep.H1("START")
    rep.line()
    rep.H2('Test data')
    # rep.create_property("property", "value")
    # rep.create_property('mode', mode)
    # rep.create_property('loop', current_loop)
    # rep.create_property('index', idx)
    # rep.create_property('sensor data path',
    #                     'c:\\data\\test\\another test\\ and yet anotherr.')

    d1 = datetime.datetime.now().replace(microsecond=0)
    time.sleep(3)
    d2 = datetime.datetime.now().replace(microsecond=0)

    rep.report_timing(d1, d2)
    rep.create_table(
        ("property", "value"),
        ('mode', mode),
        ('loop', current_loop),
        ('index', idx),
        (
            'sensor data path',
            'c:\\data\\test\\another test\\ and yet anotherr.')

    )
    rep.line()
    print("result: *FAIL*")
    rep.line()
    # rep.create_table(('property', 'value'), (1, 2), (3, 4))
