from enum import Enum
from os import path


class TargetVarsCalcWay(Enum):
    # 目标变量的计算方法
    # 计数
    COUNT = 'count'
    # 求和
    SUM = 'sum'
    # 算比例（两列相除）
    RATIO = 'ratio'
    # 算相对比例（两列相除）
    RATIO_REL = 'rel_ratio'
    # 均值
    AVERAGE = 'mean'


class DSType(Enum):
    PKL = 'pkl'
    EXCEL = 'xlsx'
    CSV = 'csv'


REPORT_PREFIX = 'urs报告'

REPORT_FOLDER = './urs_reports'

# 数据集目录
DS_FOLDER = './data_sources'

# 解析csv或者excel时备选的编码方式
DS_ENCODINGS = ('utf-8', 'gbk')

###################### 通用配置（需要根据数据集以及输出的变量进行修改） ######################
DS_FILE_NAME = './全变量(2014-2017数据集)_2018_06_11_15_20.csv'

DS_FILE_PATH = path.join(DS_FOLDER, DS_FILE_NAME)

DS_TYPE = DSType.CSV

# urs报告中的目标变量
TARGET_VARS = ['车牌号', '标准保费', '已报赔款', 'loss_cap_500k', 'cap车均赔款', 'uncap车均赔款',
               'capped_lr', 'uncapped_lr', 'capped_lr_rel', 'uncapped_lr_rel']

TARGET_VARS_IN_CHART = ['capped_lr_rel', 'uncapped_lr_rel']

# urs报告中每一列的计算方式，orig_col指定原始数据集中的列，如果求比例请用(col1, col2)表示col1/col2
TARGET_VARS_CALC_CONFIG = {
    '车牌号': {'orig_cols': '车牌号', 'calc_way': TargetVarsCalcWay.COUNT},
    '标准保费': {'orig_cols': '标准保费', 'calc_way': TargetVarsCalcWay.SUM},
    '已报赔款': {'orig_cols': '已报赔款', 'calc_way': TargetVarsCalcWay.SUM},
    'loss_cap_500k': {'orig_cols': 'loss_cap_500k', 'calc_way': TargetVarsCalcWay.SUM},
    'cap车均赔款': {'orig_cols': 'loss_cap_500k', 'calc_way': TargetVarsCalcWay.AVERAGE},
    'uncap车均赔款': {'orig_cols': '已报赔款', 'calc_way': TargetVarsCalcWay.AVERAGE},
    'capped_lr': {'orig_cols': ('loss_cap_500k', '标准保费'), 'calc_way': TargetVarsCalcWay.RATIO},
    'uncapped_lr': {'orig_cols': ('已报赔款', '标准保费'), 'calc_way': TargetVarsCalcWay.RATIO},
    'capped_lr_rel': {'orig_cols': ('loss_cap_500k', '标准保费'), 'calc_way': TargetVarsCalcWay.RATIO_REL},
    'uncapped_lr_rel': {'orig_cols': ('已报赔款', '标准保费'), 'calc_way': TargetVarsCalcWay.RATIO_REL}}

# 需要被当做枚举变量处理的
NUMERIC_VARS_AS_ENUM = ['保单年']

# 数值变量切分的分位点数量
NUMERIC_VAR_QUANTILE = 10

# 枚举变量最多显示的列数（默认排序按照变量字母顺序升序排列）
ENUM_VAR_MAX_LINES = 20

# 枚举变量按照升序排列的列
ENUM_VARS_ASCENDING_STANDARD = 'capped_lr_rel'

# 自变量的分类展示
VARS_GROUPS = {'从车因素': ['veh_age', '车辆类别'],
               '违章因素': ['Vio0-6', 'Vio7-12'],
               '保单因素': ['保单年', '被保人性别']}

######################  专用配置（根据当前的数据集类型csv or pickle 进行配置） ######################

# DATA SOURCE来自于CSV文件时需要的配置
# 需要跳过的head行配置（可能文件头部有一些说明列不需要LOAD到DataFrame当中
# 例如要跳过0，2，3，4行，SKIP_ROWS = [0, 2, 3, 4] (行数下标从0开始计算）
SKIP_ROWS = []
# 需要LOAD的列编号
# 例如需要使用第1到第63列，可以使用USE_COLS = range(1, 63)
USE_COLS = None
