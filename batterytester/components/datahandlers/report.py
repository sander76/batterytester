import logging
import os
from typing import Optional
from datetime import datetime

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import (
    FileBasedDataHandler
)
from batterytester.core.helpers.constants import RESULT_FAIL, RESULT_PASS
from batterytester.core.helpers.helpers import get_time_string
from batterytester.core.helpers.message_data import (
    FatalData,
    TestFinished,
    TestData,
    AtomData,
    AtomResult,
    TestSummary,
)
from batterytester.core.helpers.message_subjects import Subscriptions

SUMMARY_FILE_FORMAT = "{}.md"

ITALIC_FORMAT = "*{}*"
BOLD_FORMAT = "**{}**"
DL_VALUE_FORMAT = ":   {}"
BLOCKQUOTE_FORMAT = "> {}"
PROPERTY_FORMAT = "{} : {}"
COL1_WIDTH = 30
MIN_COL_WIDTH = 3
TEXT_WIDTH = 80
PROPERTY_WIDTH = 30

LOGGER = logging.getLogger(__name__)


def _header(content, level):
    return ("#" * level) + " " + content


def italic(content):
    return ITALIC_FORMAT.format(content), False


def bold(content):
    return BOLD_FORMAT.format(content), False


def block_quote(content):
    return BLOCKQUOTE_FORMAT.format(content), True


class MarkDownReport(FileBasedDataHandler):
    def __init__(
        self,
        report_name=None,
        output_path="reports",
        subscriptions: Optional[Subscriptions] = None,
    ):
        """

        :param report_name: Optional name of the report.
            By default the name of the test is used.
        :param output_path: Path to store the report file.
            Can be relative or absolute.
        """
        super().__init__(report_name, output_path, subscriptions=subscriptions)
        self.start_time = None
        self.stop_time = None
        self._test_summary = TestSummary()

    def _check_block(self):
        if not self._report_data or self._report_data[-1] != "":
            self._report_data.append("")

    def _empty_line(self):
        self._report_data.append("")

    def _create_summary_file(self):
        """Create a report file"""

        with open(self._filename, "w") as fl:
            fl.write("TEST SUMMARY FILE.\n\n")

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
    """A markdown report data handler."""

    # def __init__(self, subscriptions: Optional[Subscriptions] = None):
    #     super().__init__(subscriptions=subscriptions)
    #     self.subscriptions = (
    #         (subj.TEST_WARMUP, self._test_warmup),
    #         (subj.TEST_FATAL, self._test_fatal),
    #         (subj.TEST_FINISHED, self._test_finished),
    #         (subj.ATOM_WARMUP, self._atom_warmup),
    #         (subj.ATOM_RESULT, self._atom_result),
    #     )

    async def shutdown(self, bus):
        self._create_summary()
        await super().shutdown(bus)

    def event_test_warmup(self, testdata):
        """Create a file and write headers"""
        LOGGER.debug("test_warmup called")
        self._create_summary_file()
        self.header1("TEST : {}".format(self.test_name))
        self.start_time = datetime.fromtimestamp(testdata.started.value)
        self.create_property("START", get_time_string(self.start_time))
        self.create_property("TEST NAME", testdata.test_name.value)
        self.create_property("LOOPS", testdata.loop_count.value)

    def event_test_finished(self, testdata):
        self.stop_time = datetime.fromtimestamp(testdata.time_finished.value)

    def event_test_fatal(self, testdata):
        LOGGER.debug("test fatal called")
        super().event_test_fatal(testdata)
        self.header1("FATAL ERROR")
        self.create_property("REASON", testdata.reason.value)

    def event_atom_warmup(self, testdata):
        LOGGER.debug("atom_warmup called")
        super().event_atom_warmup(testdata)
        self.header2("TEST ATOM")
        self.create_property(
            "STARTED", datetime.fromtimestamp(testdata.started.value)
        )
        self.create_property("ATOMNAME", self._atom_name)
        self.create_property("CURRENT LOOP", self._current_loop)
        self.create_property("CURRENT INDEX", self._current_idx)

        self._flush()

    def event_atom_result(self, testdata):
        super().event_atom_result(testdata)
        _passed = testdata.passed.value
        if _passed:
            self.create_property("RESULT", RESULT_PASS)
            self._test_summary.atom_passed()
        else:
            self.create_property("RESULT", RESULT_FAIL)
            self._test_summary.atom_failed(
                self._current_idx,
                self._current_loop,
                self._atom_name,
                testdata.reason.value,
            )

    # def _atom_result(self, subject, data: AtomResult):
    #     _passed = data.passed.value
    #     if _passed:
    #         self.create_property("RESULT", RESULT_PASS)
    #         self._test_summary.atom_passed()
    #     else:
    #         self.create_property("RESULT", RESULT_FAIL)
    #         self._test_summary.atom_failed(
    #             self._current_idx,
    #             self._current_loop,
    #             self._atom_name,
    #             data.reason.value,
    #         )
    #         # self._test_summary.append(
    #         #     {'loop': self._current_loop,
    #         #      'index': self._current_idx,
    #         #      'reason': data[REASON][KEY_VALUE]})

    def _create_summary(self):
        self.header2("SUMMARY")
        self.create_property("passed", self._test_summary.passed.value)
        self.create_property("failed", self._test_summary.failed.value)
        for fails in self._test_summary.failed_ids.value:
            for key, value in fails.items():
                self.create_property(key, value)
            self._empty_line()

    def write_summary_to_file(self):
        if os.path.exists(self._filename):
            _mode = "a"
        else:
            _mode = "w"
        with open(self._filename, _mode) as fl:
            fl.write("\n".join(self._report_data))
        # reset the summary
        self._report_data = []

    # def report_timing(self, start, stop):
    #     _header = ('started', 'stopped', 'duration[seconds]')
    #     _row = (str(start), str(stop), str((stop - start).total_seconds()))
    #     self.create_table(_header, _row)

    def summarize_result(self, summary_table):
        pass
