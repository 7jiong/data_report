# coding:utf-8
# !/usr/bin/python3
import collections
import datetime
import os

import numpy as np
import pandas as pd
from bottle import template

from format_config import (COLS_TYPE, COLS_TYPE_SHOW_DESC, PATH_TO_DATA, COLS_FORCED_TO_STR, FILL_NAN_WITH_BLANK,
                           HEAD_LINE_NUM, SKIP_ROWS, USE_COLS, HEAD_NUM_CONTINUS_VAR, LIMIT_DISCRETE_COLS,
                           HEAD_NUM_DISCRETE_VAR, REPORT_PREFIX, DATA_SOURCE_TYPE, DS_ENCODINGS)


# TODO（lujia）: add navigation sidebar for quick scan
class DataFrameInfo(object):
    """
    Store marco information of DataFrame

    :attribute orig_df:  original DataFrame.
    :attribute df:  DataFrame after rearranging columns order via alphabet.
    :attribute cols_num:  number of columns.
    :attribute records_num:  number of record.
    :attribute cols:  an ordered dict stored mapping from column_name to column information.
    :attribute numeric_cols_desc:  marco description of numeric columns status.
    :attribute str_cols_desc:  marco description of str columns status.
    :attribute head_rows:  data of head rows.
    :attribute orig_df_col_to_idx:  an dict stored mapping from column_name to columns_index in orig_df.
    :attribute df_name:  name parsed from path_to_df.
    """

    def __init__(self, orig_df, df, cols_num, records_num, cols, numeric_cols_desc, str_cols_desc, head_rows,
                 orig_df_col_to_idx, df_name):
        self.orig_df = orig_df
        self.df = df
        self.cols_num = cols_num
        self.records_num = records_num
        self.cols = cols
        self.numeric_cols_desc = numeric_cols_desc
        self.str_cols_desc = str_cols_desc
        self.head_rows = head_rows
        self.orig_df_col_to_idx = orig_df_col_to_idx
        self.df_name = df_name

    @classmethod
    def _setup_df_cols(cls, df):
        """
        setup the mapping from column name to DataFrameColsInfo instance

        :return:  A dict with column name as key and DataFrameColsInfo instance as value
        """
        cols = collections.OrderedDict()
        for col_name in df.columns.tolist():
            print(col_name)
            cols[col_name] = DataFrameColsInfo(col_name, df, COLS_TYPE_SHOW_DESC)
        return cols

    @classmethod
    def _get_numeric_cols_desc(cls, records_num, df):
        """
        calculate the macro statistics information of numeric columns 

        :return:  A list with tuple element to store macro statistics information of numeric columns.
                Each tuple with index and a dict. 
        """
        numeric_cols = df.describe().T
        numeric_cols['# MISSING'] = records_num - numeric_cols['count']
        numeric_cols['10%'] = df.quantile(0.1)
        numeric_cols['20%'] = df.quantile(0.2)
        numeric_cols['30%'] = df.quantile(0.3)
        numeric_cols['40%'] = df.quantile(0.4)
        numeric_cols['50%'] = df.quantile(0.5)
        numeric_cols['60%'] = df.quantile(0.6)
        numeric_cols['70%'] = df.quantile(0.7)
        numeric_cols['80%'] = df.quantile(0.8)
        numeric_cols['90%'] = df.quantile(0.9)
        numeric_cols['100%'] = df.quantile(1)
        return zip(numeric_cols.index, numeric_cols.fillna(0).to_dict(orient='records'))

    @classmethod
    def _get_str_cols_desc(cls, cols, records_num):
        """
        calculate the macro statistics information of str columns
        contain record MISSING and NOMISSING count
             
        :return:  A list with tuple element to store macro statistics information of str columns.
                Each tuple with index and a dict.
        """
        str_cols_desc = []
        for col_name, col in cols.items():
            per_str_col_desc = {}
            if col.type_code != COLS_TYPE.NUMERIC:
                per_str_col_desc['# MISSING'] = col.df[col_name].isnull().sum()
                per_str_col_desc['# NONMISSING'] = records_num - per_str_col_desc['# MISSING']
                str_cols_desc.append((col_name, per_str_col_desc))
        return str_cols_desc

    @classmethod
    def _get_head_rows(cls, fill_nan_with_blank, head_line_num, df):
        """
        get head records for displaying example data in report 

        :param fill_nan_with_blank:  specify whether fill nan with blank line
        :return:  A list with tuple element to store example data in report.
                Each tuple with index and a dict. 
        """
        if fill_nan_with_blank:
            return zip(df.index.tolist(), df.head(head_line_num).fillna('').to_dict(orient='records'))
        else:
            return zip(df.index.tolist(), df.head(head_line_num).to_dict(orient='records'))

    @classmethod
    def _force_convert_numeric_col_to_str(cls, cols_forced_to_str, df):
        """
        forced specified columns from numeric type to str type inplace

        :param cols_forced_to_str:  list force turn numeric type to string
        :return: 
        """
        for col_name in cols_forced_to_str:
            df[col_name] = df[col_name].astype(str)
        return df

    @classmethod
    def create_df_info_from_ascill(cls, read_func, path=PATH_TO_DATA,
                                   cols_forced_to_str=COLS_FORCED_TO_STR,
                                   fill_nan_with_blank=FILL_NAN_WITH_BLANK,
                                   head_line_num=HEAD_LINE_NUM,
                                   skip_rows=SKIP_ROWS,
                                   use_cols=USE_COLS):
        """create DataFrame from csv file"""
        orig_df = None
        for encoding in DS_ENCODINGS:
            try:
                orig_df = read_func(path, skiprows=skip_rows, usecols=use_cols, encoding=encoding)
            except Exception as e:
                print(e)
                continue
            else:
                break
        if orig_df is None:
            raise QCException('Error! coding type not included in ENCONDINGS_PENDING!')
        return cls.create_df_comm_op(orig_df=orig_df, path=path, cols_forced_to_str=cols_forced_to_str,
                                     fill_nan_with_blank=fill_nan_with_blank, head_line_num=head_line_num)

    @classmethod
    def create_df_info_from_pickle(cls, path=PATH_TO_DATA,
                                   cols_forced_to_str=COLS_FORCED_TO_STR,
                                   fill_nan_with_blank=FILL_NAN_WITH_BLANK,
                                   head_line_num=HEAD_LINE_NUM):

        """create DataFrame from pickle file
        :param
        :path  
        """

        orig_df = pd.read_pickle(path)
        return cls.create_df_comm_op(orig_df=orig_df, path=path, cols_forced_to_str=cols_forced_to_str,
                                     fill_nan_with_blank=fill_nan_with_blank, head_line_num=head_line_num)

    @classmethod
    def create_df_comm_op(cls, orig_df, path, cols_forced_to_str, fill_nan_with_blank, head_line_num):
        # 按字母序排列DataFrame的列
        df = orig_df.reindex(sorted(orig_df.columns), axis=1)
        # 强制转换几个变量类型 numeric -> str
        df = cls._force_convert_numeric_col_to_str(cols_forced_to_str=cols_forced_to_str, df=df)
        cols_num = df.shape[1]
        records_num = df.shape[0]
        cols = cls._setup_df_cols(df=df)
        numeric_cols_desc = cls._get_numeric_cols_desc(records_num=records_num, df=df)
        str_cols_desc = cls._get_str_cols_desc(cols=cols, records_num=records_num)
        head_rows = cls._get_head_rows(fill_nan_with_blank=fill_nan_with_blank,
                                       head_line_num=head_line_num,
                                       df=df)
        # 保留原始DataFrame中的列名和列下标的关系
        orig_df_col_to_idx = dict(zip(orig_df.columns.tolist(), range(0, cols_num)))
        df_name = os.path.split(path)[-1].split('.')[0]
        return cls(orig_df=orig_df, df=df, cols_num=cols_num, records_num=records_num, cols=cols,
                   numeric_cols_desc=numeric_cols_desc, str_cols_desc=str_cols_desc, head_rows=head_rows,
                   orig_df_col_to_idx=orig_df_col_to_idx, df_name=df_name)


class DataFrameColsInfo(object):
    """
    Store information of each column

    :attribute col_name:  column name
    :attribute df:  DataFrame
    :attribute isnumeric:  type of columns enum(NUMERIC=1, STR=2, TIME=3)
    :attribute type:  column's dtype.
    :attribute type_length:  memory space used.
    :attribute df_desc:  column data distribution info
    """

    def __init__(self, col_name, df, cols_type_show_desc):
        self.col_name = col_name
        self.df = df
        self.type_code = self._cal_col_type_code()
        self.type = df[col_name].dtype
        self.type_length = self._cal_col_dtype_length(self.type_code)
        self.df_desc = self._cal_head_records_desc(self.type_code, cols_type_show_desc)

    def _cal_head_records_desc(self, type_code, cols_type_show_desc):
        """calculate the values with high frequency in current column
                
        :param type_code:  column type enum(NUMERIC=1, STR=2, TIME=3)     
        :param cols_type_show_desc:  specify some columns type to display statistical description
        :return:  A list with tuple element to store high frequency record.
                Each tuple with index and a dict. For
                example:
                    [(0,{'freq':0,'freq_percentage':0,'cum_freq':0,'cum_freq_percentage':0}),
                    (1,{'freq':0,'freq_percentage':0,'cum_freq':0,'cum_freq_percentage':0}),]
        """
        if type_code not in cols_type_show_desc:
            return
        df_desc = pd.DataFrame()
        if type_code == COLS_TYPE.NUMERIC:
            df_desc['freq'] = self.df[self.col_name].value_counts(dropna=False).iloc[:HEAD_NUM_CONTINUS_VAR]
            df_desc.index = df_desc.index.map(lambda x: x if np.isnan(x) else round(x, 2))
        else:
            if self.col_name in LIMIT_DISCRETE_COLS:
                df_desc['freq'] = self.df[self.col_name].value_counts(dropna=False).iloc[:HEAD_NUM_DISCRETE_VAR]
            else:
                df_desc['freq'] = self.df[self.col_name].value_counts(dropna=False)
        df_desc['freq_percentage'] = df_desc['freq'] / len(self.df[self.col_name])
        df_desc['cum_freq'] = df_desc['freq'].cumsum(skipna=False)
        df_desc['cum_freq_percentage'] = df_desc['cum_freq'] / len(self.df[self.col_name])

        if FILL_NAN_WITH_BLANK:
            return zip(df_desc.index.fillna('').tolist(), df_desc.fillna('').to_dict(orient='records'))
        else:
            return zip(df_desc.index.tolist(), df_desc.to_dict(orient='records'))

    def _cal_col_dtype_length(self, type_code):
        """
        calculate the length of column data
                
        :param type_code:  column type enum(NUMERIC=1, STR=2, TIME=3)
        :return:  length of column data
        """
        if type_code == COLS_TYPE.STR:
            return ""
        else:
            return self.type.itemsize

    def _cal_col_type_code(self):
        """
        calculate the data type of column
                
        :return:  column data type: NUMERIC=1, STR=2, TIME=3
        """
        if self.df[self.col_name].dtype in [np.float64, np.int64]:
            return COLS_TYPE.NUMERIC
        elif self.df[self.col_name].dtype == np.dtype('<M8[ns]'):
            return COLS_TYPE.TIME
        else:
            return COLS_TYPE.STR


class ReportInfo(object):
    """
    Class storing information of each column
        
    :attribute df_info: instance of DataFrameInfo
    :attribute process_time:  report generate time
    """

    def __init__(self, df_info):
        self.df_info = df_info
        self.process_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def create_from_data_frame_info(cls, data_source_type):
        if data_source_type == DATA_SOURCE_TYPE.PICKLE:
            df_info = DataFrameInfo.create_df_info_from_pickle()
        elif data_source_type == DATA_SOURCE_TYPE.CSV:
            df_info = DataFrameInfo.create_df_info_from_ascill(read_func=pd.read_csv)
        elif data_source_type == DATA_SOURCE_TYPE.EXCEL:
            df_info = DataFrameInfo.create_df_info_from_ascill(read_func=pd.read_excel)
        else:
            raise QCException(f'{data_source_type} does not support currently!')
        return cls(df_info=df_info)

    def to_html(self):
        html = template("./report_template.html", data_quality_checker=self)
        fname = "%s_%s_%s.html" % (REPORT_PREFIX, self.df_info.df_name, self.process_time)
        fpath = os.path.join('dataQualityReports', fname)
        with open(fpath, 'wb') as f:
            f.write(html.encode('utf-8'))


class QCException(Exception):
    pass
