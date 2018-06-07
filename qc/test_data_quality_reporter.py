# coding:utf-8
# !/usr/bin/python3
#
# Created by Lujia Zhang (2017)
#
#
# unittest for data_quality_reporter
import collections
import datetime
import unittest

import numpy as np
import pandas as pd

import format_config
from data_quality_reporter import DataFrameInfo, DataFrameColsInfo


class TestDataFrameInfo(unittest.TestCase):
    def setUp(self):
        s_numeric = pd.Series(np.array([1, 2, 3]))
        s_numeric2 = pd.Series(np.array([4, 5, 6]))
        s_str = pd.Series(np.array(['a', 'b', 'c']))
        s_time = pd.Series(
            [datetime.datetime(2011, 1, 1), datetime.datetime(2011, 1, 2), datetime.datetime(2011, 1, 3)])
        test_orig_df = pd.DataFrame({'numeric': s_numeric, 'numeric2': s_numeric2, 'str': s_str, 'time': s_time})
        self.df_info = DataFrameInfo.create_df_comm_op(orig_df=test_orig_df, path='test',
                                                       cols_forced_to_str=['numeric'],
                                                       fill_nan_with_blank=True, head_line_num=20)

    def test_setup_df_cols(self):
        cols = collections.OrderedDict()
        for col_name in self.df_info.df.columns.tolist():
            cols[col_name] = DataFrameColsInfo(col_name, self.df_info.df,
                                               [format_config.COLS_TYPE.NUMERIC])
        self.assertEqual(cols.keys(), self.df_info.cols.keys())

    def test_get_numeric_cols_desc(self):
        numeric_cols = self.df_info.df.describe().T
        numeric_cols['# MISSING'] = self.df_info.records_num - numeric_cols['count']
        for i in range(10):
            numeric_cols[f'{(i+1)*10}%'] = self.df_info.df.quantile((i + 1) / 10)
        numeric_col_desc = zip(numeric_cols.index, numeric_cols.fillna(0).to_dict(orient='records'))

        for (_, content_left), (_, content_right) in zip(numeric_col_desc, self.df_info.numeric_cols_desc):
            self.assertEqual(content_left, content_right)

    def test_get_str_cols_desc(self):
        str_cols_desc = []
        for col_name, col in self.df_info.cols.items():
            per_str_col_desc = {}
            if col.type_code != format_config.COLS_TYPE.NUMERIC:
                per_str_col_desc['# MISSING'] = col.df[col_name].isnull().sum()
                per_str_col_desc['# NONMISSING'] = self.df_info.records_num - per_str_col_desc['# MISSING']
                str_cols_desc.append((col_name, per_str_col_desc))
        self.assertEqual(str_cols_desc, self.df_info.str_cols_desc)

    def test_get_head_rows(self):
        head_rows = zip(self.df_info.df.index.tolist(),
                        self.df_info.df.head(format_config.HEAD_LINE_NUM).to_dict(orient='records'))
        for (_, content_left), (_, content_right) in zip(head_rows, self.df_info.head_rows):
            self.assertEqual(content_left, content_right)

    def test_force_convert_numeric_col_to_str(self):
        self.assertEqual(self.df_info.df['numeric'].dtype, object)


class TestDataFrameColsInfo(unittest.TestCase):
    def setUp(self):
        s_numeric = pd.Series(np.array([1, 2, 3]))
        s_numeric2 = pd.Series(np.array([4, 5, 6]))
        s_str = pd.Series(np.array(['a', 'b', 'c']))
        s_time = pd.Series(
            [datetime.datetime(2011, 1, 1), datetime.datetime(2011, 1, 2), datetime.datetime(2011, 1, 3)])
        test_orig_df = pd.DataFrame({'numeric': s_numeric, 'numeric2': s_numeric2, 'str': s_str, 'time': s_time})
        self.df_info = DataFrameInfo.create_df_comm_op(orig_df=test_orig_df, path='test',
                                                       cols_forced_to_str=['numeric'],
                                                       fill_nan_with_blank=True, head_line_num=20)

    def test_cal_head_records_desc(self):
        target_res = [(6, {'cum_freq_percentage': 0.3333333333333333,
                           'freq': 1.0, 'cum_freq': 1.0,
                           'freq_percentage': 0.3333333333333333}),
                      (5, {'cum_freq_percentage': 0.6666666666666666,
                           'freq': 1.0, 'cum_freq': 2.0,
                           'freq_percentage': 0.3333333333333333}),
                      (4, {'cum_freq_percentage': 1.0,
                           'freq': 1.0,
                           'cum_freq': 3.0,
                           'freq_percentage': 0.3333333333333333})]

        for (_, content_left), (_, content_right) in zip(target_res, self.df_info.cols['numeric2'].df_desc):
            self.assertEqual(content_left, content_right)

    def test_cal_col_type_code(self):
        self.assertEqual(self.df_info.cols['numeric'].type_code, format_config.COLS_TYPE.STR)
        self.assertEqual(self.df_info.cols['numeric2'].type_code, format_config.COLS_TYPE.NUMERIC)
        self.assertEqual(self.df_info.cols['str'].type_code, format_config.COLS_TYPE.STR)
        self.assertEqual(self.df_info.cols['time'].type_code, format_config.COLS_TYPE.TIME)


if __name__ == '__main__':
    unittest.main()
