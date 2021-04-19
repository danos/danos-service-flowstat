#!/usr/bin/env python3
#
# Copyright (c) 2021, SafePoint <info@safepoint.vn>.  All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

import os
import unittest
from flowstat import FlowStatDb

_base_dir = os.path.abspath(__file__ + '/../')


def _abs_path(path):
    return os.path.abspath(os.path.join(_base_dir, path))


class TestQuery(unittest.TestCase):
    def test_query_top_src(self):
        db = FlowStatDb(':memory:')
        db.connect()
        db.collect_from_logfile(_abs_path('data/2.log'))

        res = db.query_top('src', 'bytes', 1615434285, 1615434288)
        assert len(res) == 2
        item = res[0]
        assert item['key'] == '192.168.100.214'
        assert item['in_bytes'] == 953
        assert item['out_bytes'] == 619
        assert item['bytes'] == 1572

        db.close()

    def test_query_timeseries(self):
        db = FlowStatDb(':memory:')
        db.connect()
        db.collect_from_logfile(_abs_path('data/2.log'))

        res = db.query_time_series('src', 1615434285, 1615434288)
        assert len(res) == 1
        item = res[0]
        assert item['timestamp'] == 1615434280
        assert item['in_bytes'] == 1981
        assert item['out_bytes'] == 922
        assert item['bytes'] == 2903

        db.close()

    def test_query_top_src_intf(self):
        db = FlowStatDb(':memory:')
        db.connect()
        db.collect_from_logfile(_abs_path('data/logintf.log'))

        res = db.query_top('src', 'bytes', 1615434285, 1615434288,
                           if_name='dp0p33p1')
        assert len(res) == 1
        item = res[0]
        assert item['key'] == '192.168.100.79'
        assert item['in_bytes'] == 1028
        assert item['out_bytes'] == 303
        assert item['bytes'] == 1331

        db.close()

    def test_query_timeseries_intf(self):
        db = FlowStatDb(':memory:')
        db.connect()
        db.collect_from_logfile(_abs_path('data/logintf.log'))

        res = db.query_time_series('src', 1615434285, 1615434288,
                                   if_name='dp0p33p1')
        assert len(res) == 1
        item = res[0]
        assert item['timestamp'] == 1615434280
        assert item['in_bytes'] == 1028
        assert item['out_bytes'] == 303
        assert item['bytes'] == 1331

        db.close()

    def test_query_timeseries_key(self):
        db = FlowStatDb(':memory:')

        db.connect()
        db.collect_from_logfile(_abs_path('data/2.log'))

        res = db.query_time_series('src', 1615434285, 1615434288,
                                   if_name='dp0p33p1',
                                   filter_key='192.168.100.214')
        assert len(res) == 1
        item = res[0]
        assert item['timestamp'] == 1615434280
        assert item['in_bytes'] == 953
        assert item['out_bytes'] == 619
        assert item['bytes'] == 1572

        db.close()


class TestReadLog(unittest.TestCase):
    def test_read_limit(self):
        db = FlowStatDb(':memory:', read_limit=1, read_limit_interval=0)
        db.connect()

        # read
        db.collect_from_logfile(_abs_path('data/2.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 1615434287

        db.close()

    def test_read_limit_2(self):
        db = FlowStatDb(':memory:', read_limit=1, read_limit_interval=0)
        db.connect()

        # read
        db.collect_from_logfile(_abs_path('data/readlimit.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 271
        assert db.last_log['timestamp'] == 1615434290

        db.close()

    def test_last_logfile(self):
        db = FlowStatDb(':memory:')
        db.connect()

        # read
        db.collect_from_logfile(_abs_path('data/lastfile.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 1615434287

        db.close()

    def test_last_log_again(self):
        db = FlowStatDb(':memory:')
        db.connect()

        # read 2 times
        db.collect_from_logfile(_abs_path('data/lastfile.log'))
        db.collect_from_logfile(_abs_path('data/lastfile.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 1615434287

        db.close()

    def test_last_logfile_position(self):
        db = FlowStatDb(':memory:')
        db.connect()

        # read
        db.collect_from_logfile(_abs_path('data/lastfile2.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 271
        assert db.last_log['timestamp'] == 1615434290

        db.close()

    def test_find_last_logfile(self):
        db = FlowStatDb(':memory:')
        db.connect()

        db._load_metadata()
        db.last_log['index'] = 0
        db.last_log['position'] = 0
        db.last_log['timestamp'] = 1615434287
        db._save_metadata()

        db.find_last_logfile(_abs_path('data/lastfile.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 1615434287

        db.close()

    def test_find_last_logfile_rotate(self):
        db = FlowStatDb(':memory:')
        db.connect()

        # info of old log file
        db.last_log['index'] = 0
        db.last_log['position'] = 0
        db.last_log['timestamp'] = 1615434287
        db._save_metadata()

        db.find_last_logfile(_abs_path('data/rotate.log'))

        assert db.last_log['index'] == 1
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 1615434287

        db.close()

    def test_find_last_logfile_wrong_index(self):
        db = FlowStatDb(':memory:')
        db.connect()

        db.last_log['index'] = 1
        db.last_log['position'] = 0
        db.last_log['timestamp'] = 1615434287
        db._save_metadata()

        db.find_last_logfile(_abs_path('data/lastfile.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 1615434287

        db.close()

    def test_find_last_logfile_wrong_index_timestamp(self):
        db = FlowStatDb(':memory:')
        db.connect()

        db.last_log['index'] = 1
        db.last_log['position'] = 0
        db.last_log['timestamp'] = 9999
        db._save_metadata()

        db.find_last_logfile(_abs_path('data/lastfile.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 0

        db.close()

    def test_find_last_logfile_wrong_position(self):
        db = FlowStatDb(':memory:')
        db.connect()

        db.last_log['index'] = 0
        db.last_log['position'] = 9999
        db.last_log['timestamp'] = 1615434287
        db._save_metadata()

        db.find_last_logfile(_abs_path('data/lastfile.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 0

        db.close()

    def test_find_last_logfile_wrong_timestamp(self):
        db = FlowStatDb(':memory:')
        db.connect()

        db.last_log['index'] = 0
        db.last_log['position'] = 0
        db.last_log['timestamp'] = 9999
        db._save_metadata()

        db.find_last_logfile(_abs_path('data/lastfile.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 0

        db.close()

    def test_read_two_rotate_logfile_jump_next(self):
        db = FlowStatDb(':memory:')
        db.connect()

        # info of old log file
        db.last_log['index'] = 0
        db.last_log['position'] = 0
        db.last_log['timestamp'] = 1615434287
        db._save_metadata()

        # read next
        db.collect_from_logfile(_abs_path('data/rotate.log'))

        assert db.last_log['index'] == 0
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 1615434290

        db.close()

    def test_read_two_rotate_logfile_not_jump(self):
        db = FlowStatDb(':memory:')
        db.connect()

        # info of old log file
        db.last_log['index'] = 0
        db.last_log['position'] = 0
        db.last_log['timestamp'] = 1615434287
        db._save_metadata()

        # read new
        db.collect_from_logfile(_abs_path('data/rotate2.log'))

        assert db.last_log['index'] == 1
        assert db.last_log['position'] == 0
        assert db.last_log['timestamp'] == 1615434287

        db.close()


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    unittest.main()
