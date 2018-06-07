# coding:utf-8
# !/usr/bin/python3
#
# Created by Lujia Zhang (2017)
#
#
# config file control report format


def enum(**enums):
    return type('Enum', (), enums)


###################### 默认配置（一般情况不用修改） ######################

# 数据集支持的格式(CSV和PICKLE)
DATA_SOURCE_TYPE = enum(CSV=1, PICKLE=2)

# 数据集的变量类型（NUMERIC, STR, TIME）
COLS_TYPE = enum(NUMERIC=1, STR=2, TIME=3)

# 需要显示统计信息的变量类型, 默认时间变量不参与qc统计
COLS_TYPE_SHOW_DESC = [COLS_TYPE.STR, COLS_TYPE.NUMERIC]

# 生成的URS报告前缀名
REPORT_PREFIX = "dataQualityReport"

# 报告中NAN和NAT的字段是否显示为空白
FILL_NAN_WITH_BLANK = True

# 样本数据部分中需要显示的原始数据记录数
HEAD_LINE_NUM = 20

# 数值型变量在频数统计时显示的行数
HEAD_NUM_CONTINUS_VAR = 20

# 离散型变量在频数统计时显示的行数(防止数量太多刷屏）
HEAD_NUM_DISCRETE_VAR = 20

######################  通用配置（每次选择不同数据集的时候，需要按需调整） ######################

# 原始数据集的路径
PATH_TO_DATA = "/Users/hzzlj/Desktop/Projects/dm/安华农/安华农数据步骤整理/step_15_合并违章数据_2014_2016.pkl"

# 默认的数据格式PICKLE, 可以根据需要更改为数据集支持的格式
DATA_SOURCE = DATA_SOURCE_TYPE.PICKLE

# 需要强制转换为STR的列的列表, 例如["Credit-No", "Dealer", "DefectCode"]
COLS_FORCED_TO_STR = []

# 列表中的离散变量最多展示《默认配置》中HEAD_NUM_DISCRETE_VAR数量的行数
LIMIT_DISCRETE_COLS = ['被保人姓名', '车主姓名', '车型代码', '车牌号', '车系代码', '车系名称', '车队代码',
                       '品牌代码', '品牌名称', '车型名称', 'VIN码', 'brand', '发动机号']

######################  专用配置（根据当前的数据集类型csv or pickle 进行配置） ######################

# DATA SOURCE来自于CSV文件时需要的配置
# 需要跳过的head行配置（可能文件头部有一些说明列不需要LOAD到DataFrame当中
SKIP_ROWS = [0, 2, 3, 4]
# 需要LOAD的列编号
USE_COLS = range(1, 63)
