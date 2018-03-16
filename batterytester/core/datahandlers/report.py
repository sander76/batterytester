import logging
import os
from datetime import datetime

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.datahandlers import BaseDataHandler
from batterytester.core.helpers.constants import RESULT_FAIL, \
    RESULT_PASS
from batterytester.core.helpers.helpers import FatalTestFailException, \
    get_current_time_string, get_time_string
from batterytester.core.helpers.message_data import FatalData, TestFinished, \
    TestData, AtomData, AtomResult, TestSummary

SUMMARY_FILE_FORMAT = '{}.md'

ITALIC_FORMAT = '*{}*'
BOLD_FORMAT = '**{}**'
DL_VALUE_FORMAT = ':   {}'
BLOCKQUOTE_FORMAT = '> {}'
PROPERTY_FORMAT = '{} : {}'
COL1_WIDTH = 30
MIN_COL_WIDTH = 3
TEXT_WIDTH = 80
PROPERTY_WIDTH = 30

LOGGER = logging.getLogger(__name__)


def _header(content, level):
    return ('#' * level) + ' ' + content


def italic(content):
    return ITALIC_FORMAT.format(content), False


def bold(content):
    return BOLD_FORMAT.format(content), False


def block_quote(content):
    return BLOCKQUOTE_FORMAT.format(content), True


def create_output_location(report_sub_folder, report_name, base_path=None):
    if base_path:
        if not os.path.exists(base_path):
            raise FatalTestFailException("output base path does not exist")
    else:
        base_path = os.getcwd()
    _report_folder = os.path.join(base_path, report_sub_folder)
    os.makedirs(_report_folder)
    return os.path.join(_report_folder, report_name)


def create_report_file(test_name, report_name='report',
                       base_path=None):
    _report_name = SUMMARY_FILE_FORMAT.format(report_name)
    _report_sub_folder = "{}_{}".format(get_current_time_string(), test_name)
    return create_output_location(
        _report_sub_folder, _report_name, base_path=base_path)


class MarkDownReport(BaseDataHandler):
    def __init__(self, test_name, report_name='report', output_path=None):
        super().__init__()
        self._filename = create_report_file(
            test_name, report_name, output_path)
        self.test_name = test_name
        self.start_time = None
        self.stop_time = None
        self._test_summary = TestSummary()
        self._report_data = []  # All report lines are stored here.

    def _check_block(self):
        if not self._report_data or self._report_data[-1] != '':
            self._report_data.append('')

    def _empty_line(self):
        self._report_data.append('')

    def _create_summary_file(self):
        with open(self._filename, 'w') as fl:
            fl.write('TEST SUMMARY FILE.\n\n')

    def header1(self, content):
        self._check_block()
        self._report_data.append(_header(content, 1))
        self._empty_line()

    def header2(self, content):
        self._check_block()
        self._report_data.append(_header(content, 2))
        self._empty_line()

    def header3(self, content):
        self._check_block()
        self._report_data.append(_header(content, 3))
        self._empty_line()

    def p(self, content):
        self._check_block()
        self._report_data.append(content)
        self._empty_line()

    def create_property(self, key: str, value):
        _key_width = max(len(key), PROPERTY_WIDTH)
        _key = key.ljust(_key_width)
        _ln = PROPERTY_FORMAT.format(_key, value)
        self._report_data.append(_ln)


class Report(MarkDownReport):

    def get_subscriptions(self):
        """Returns a tuple of topics to listen for and
        corresponding methods to execute"""
        return (

            (subj.TEST_WARMUP, self._test_warmup),
            (subj.TEST_FATAL, self._test_fatal),
            (subj.TEST_FINISHED, self._test_finished),

            (subj.ATOM_WARMUP, self._atom_warmup),
            (subj.ATOM_RESULT, self._atom_result)
        )

    async def stop_data_handler(self):
        self._create_summary()
        self._flush()

    def _test_warmup(self, subject, data: TestData):
        """Create a file and write headers"""
        LOGGER.debug("test_warmup called")
        self._create_summary_file()
        self.header1("TEST : {}".format(self.test_name))
        self.start_time = datetime.fromtimestamp(
            data.started.value)
        self.create_property("START", get_time_string(self.start_time))
        self.create_property("TEST NAME", data.test_name.value)
        self.create_property("LOOPS", data.loop_count.value)

    def _test_finished(self, subject, data: TestFinished):
        self.stop_time = datetime.fromtimestamp(
            data.time_finished.value)

    def _test_fatal(self, subject, data: FatalData):
        LOGGER.debug("test fatal called")
        self.header1("FATAL ERROR")
        self.create_property("REASON", data.reason.value)

    def _atom_warmup(self, subject, data: AtomData):
        super()._atom_warmup(subject, data)
        LOGGER.debug("atom_warmup called")
        self.header2('TEST ATOM')
        self.create_property(
            "STARTED", datetime.fromtimestamp(data.started.value))
        self.create_property('ATOMNAME', self._atom_name)
        self.create_property('CURRENT LOOP', self._current_loop)
        self.create_property('CURRENT INDEX', self._current_idx)

        self._flush()

    def _atom_result(self, subject, data: AtomResult):
        _passed = data.passed.value
        if _passed:
            self.create_property('RESULT', RESULT_PASS)
            self._test_summary.atom_passed()
        else:
            self.create_property('RESULT', RESULT_FAIL)
            self._test_summary.atom_failed(
                self._current_idx,
                self._current_loop,
                self._atom_name,
                data.reason.value
            )
            # self._test_summary.append(
            #     {'loop': self._current_loop,
            #      'index': self._current_idx,
            #      'reason': data[REASON][KEY_VALUE]})

    def _create_summary(self):
        self.header2('SUMMARY')
        self.create_property('passed', self._test_summary.passed.value)
        self.create_property('failed', self._test_summary.failed.value)
        for fails in self._test_summary.failed_ids.value:
            for key, value in fails.items():
                self.create_property(key, value)
            self._empty_line()

    # def H1(self, content):
    #     self._output(header(content, 1))
    #     self.EmptyLine()

    # def H2(self, content):
    #     self._output(header(content, 2))
    #     self.EmptyLine()
    #
    # def H3(self, content):
    #     self._output(header(content, 3))
    #     self.EmptyLine()

    # def line(self, char='-'):
    #     self._output(('', char * TEXT_WIDTH, ''))
    #
    # def italic(self, content):
    #     self._output(italic(content))
    #
    # def bold(self, content):
    #     self._output(bold(content))
    #
    # def create_bordered(self, content):
    #     self.line()
    #     self.italic(content)
    #     self.line()

    # def create_dl(self, property_, value):
    #     self._output(property_)
    #     self._output(DL_VALUE_FORMAT.format(value))

    # def final_test_result(self, success: bool, reason):
    #     self.test_result(success)
    #     self._output(block_quote(reason))

    # def test_result(self, success: bool):
    #     result = 'PASS'
    #     if not success:
    #         result = 'FAIL'
    #     _content = bold(result)
    #     _content = header(_content, 2)
    #     self._output((block_quote(_content), ''))

    # def create_property_table(self, *rows):
    #     """Creates a table of key value pairs."""
    #     header = ('property', 'value')
    #     self.create_table(header, *rows)

    # def create_table(self, header, *rows, col1_width=COL1_WIDTH):
    #     _colwidths = []
    #
    #     def add_col_width(value, idx):
    #         try:
    #             _old_val = _colwidths[idx]
    #             if value > _old_val:
    #                 _colwidths[idx] = value
    #         except IndexError:
    #             if col1_width and idx == 0:
    #                 value = max(value, COL1_WIDTH)
    #             value = max(value, MIN_COL_WIDTH)
    #             _colwidths.append(value)
    #
    #     for idx, _col in enumerate(header):
    #         add_col_width(len(_col), idx)
    #     for _row in rows:
    #         for idx, _col in enumerate(_row):
    #             add_col_width(len(str(_col)), idx)
    #
    #     output = []
    #     output.append(' | '.join(
    #         (value.ljust(width) for value, width in
    #          zip(header, _colwidths))))
    #     output.append(' | '.join('-' * width for width in _colwidths))
    #
    #     for _row in rows:
    #         output.append(
    #             (' | '.join(
    #                 (str(value).ljust(width) for value, width in
    #                  zip(_row, _colwidths))
    #             )).rstrip()
    #         )
    #     # add an empty line to the end.
    #     output.append('')
    #     self._output(output)

    # def _output(self, output, block_element=False):
    #
    #     if output block_element:
    #         if not self._report_data[-1] == '':
    #             self._report_data.append('')
    #     self._report_data.append(output)

    def write_summary_to_file(self):
        if os.path.exists(self._filename):
            _mode = 'a'
        else:
            _mode = 'w'
        with open(self._filename, _mode) as fl:
            fl.write('\n'.join(self._report_data))
        # reset the summary
        self._report_data = []

    # def report_timing(self, start, stop):
    #     _header = ('started', 'stopped', 'duration[seconds]')
    #     _row = (str(start), str(stop), str((stop - start).total_seconds()))
    #     self.create_table(_header, _row)

    def summarize_result(self, summary_table):
        pass

    def _flush(self):
        """Writes buffer to file"""
        with open(self._filename, 'a') as fl:
            fl.write('\n'.join(self._report_data))
            fl.write('\n')
        # reset the summary
        self._report_data = []
