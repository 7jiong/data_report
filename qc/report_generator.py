# coding:utf-8
# !/usr/bin/python3
#
# Created by Lujia Zhang (2017)
#
# Data Qaulity Reporter (html format)
#

from data_quality_reporter import ReportInfo
from format_config import DATA_SOURCE_TYPE

if __name__ == "__main__":
    print('start to generate qc report')
    data_quality_checker = ReportInfo.create_from_data_frame_info(data_source_type=DATA_SOURCE_TYPE.PICKLE)
    data_quality_checker.to_html()
    print('finished generating qc report')
