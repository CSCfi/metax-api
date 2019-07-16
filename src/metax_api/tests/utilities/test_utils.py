# This file is part of the Metax API service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT
from django.test import TestCase

from metax_api.utils import compare_datetime, get_tz_aware_now_without_micros, \
    parse_timestamp_string_to_tz_aware_datetime


class UtilsTests(TestCase):

    def test_compare_datetime(self):
        """
        compare_datetime is called from onappstart.py only so it needs separate testcase at least for now.
        """
        testdate = parse_timestamp_string_to_tz_aware_datetime('1970-01-01T00:00:00Z')
        result = compare_datetime(testdate)
        self.assertTrue(result)

        testdate = get_tz_aware_now_without_micros()
        result = compare_datetime(testdate, delta=2)
        self.assertFalse(result)
