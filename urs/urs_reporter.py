import os
from datetime import datetime

import numpy as np
import pandas as pd

from config import (DS_FILE_PATH, NUMERIC_VARS_AS_ENUM, TARGET_VARS, TARGET_VARS_CALC_CONFIG,
                    VARS_GROUPS,
                    SKIP_ROWS, USE_COLS, NUMERIC_VAR_QUANTILE, ENUM_VAR_MAX_LINES, REPORT_PREFIX,
                    REPORT_FOLDER, DS_ENCODINGS, TARGET_VARS_IN_CHART, DSType, TargetVarsCalcWay, DS_TYPE)


class ReportGenerator:
    def __init__(self, df, path, numeric_vars_as_enum, target_vars, target_vars_in_chart, target_vars_calc_config,
                 numeric_var_quantile,
                 enum_var_max_lines, var_groups, report_prefix, report_folder):
        self.df = df
        self.df_name = os.path.split(path)[-1].split('.')[0]
        self.numeric_vars_as_enum = numeric_vars_as_enum
        self.target_vars = target_vars
        self.target_vars_calc_config = target_vars_calc_config
        self.target_vars_in_chart = target_vars_in_chart
        self.numeric_var_quantile = numeric_var_quantile
        self.enum_var_max_lines = enum_var_max_lines
        self.var_groups = var_groups
        self.report_prefix = report_prefix
        self.report_folder = report_folder
        self.process_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def create_generator_from_pickle(cls, path=DS_FILE_PATH, numeric_vars_as_enum=NUMERIC_VARS_AS_ENUM,
                                     target_vars=TARGET_VARS, target_vars_calc_config=TARGET_VARS_CALC_CONFIG,
                                     target_vars_in_chart=TARGET_VARS_IN_CHART,
                                     numeric_var_quantile=NUMERIC_VAR_QUANTILE, enum_var_max_lines=ENUM_VAR_MAX_LINES,
                                     var_groups=VARS_GROUPS, report_prefix=REPORT_PREFIX,
                                     report_folder=REPORT_FOLDER
                                     ):
        df = pd.read_pickle(path=path)
        return cls(df=df, path=path, numeric_vars_as_enum=numeric_vars_as_enum, target_vars=target_vars,
                   target_vars_calc_config=target_vars_calc_config, target_vars_in_chart=target_vars_in_chart,
                   numeric_var_quantile=numeric_var_quantile,
                   enum_var_max_lines=enum_var_max_lines, var_groups=var_groups,
                   report_prefix=report_prefix, report_folder=report_folder)

    @classmethod
    def create_generator_from_ascii(cls, read_func, path=DS_FILE_PATH, numeric_vars_as_enum=NUMERIC_VARS_AS_ENUM,
                                    target_vars=TARGET_VARS, target_vars_calc_config=TARGET_VARS_CALC_CONFIG,
                                    target_vars_in_chart=TARGET_VARS_IN_CHART,
                                    numeric_var_quantile=NUMERIC_VAR_QUANTILE, enum_var_max_lines=ENUM_VAR_MAX_LINES,
                                    var_groups=VARS_GROUPS, report_prefix=REPORT_PREFIX,
                                    report_folder=REPORT_FOLDER, skip_rows=SKIP_ROWS, use_cols=USE_COLS,
                                    encodings=DS_ENCODINGS):
        df = None
        for encoding in encodings:
            try:
                df = read_func(path, skiprows=skip_rows, usecols=use_cols, encoding=encoding)
            except Exception as e:
                print(e)
                continue
            else:
                break
        if df is None:
            raise URSException('Coding type not included in DATA_SOURCE_ENCODINGS!')

        return cls(df=df, path=path, numeric_vars_as_enum=numeric_vars_as_enum, target_vars=target_vars,
                   target_vars_calc_config=target_vars_calc_config, target_vars_in_chart=target_vars_in_chart,
                   numeric_var_quantile=numeric_var_quantile,
                   enum_var_max_lines=enum_var_max_lines, var_groups=var_groups,
                   report_prefix=report_prefix, report_folder=report_folder)

    def to_excel(self):
        excel_name = f'{self.report_prefix}_{self.df_name}_{self.process_time}.xlsx'
        excel_file = os.path.join(self.report_folder, excel_name)
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        for gname, gvars in self.var_groups.items():
            group_report_generator = GroupReportGenerator(df=self.df, writer=writer, sheet_name=gname, variables=gvars,
                                                          target_vars=self.target_vars,
                                                          target_vars_in_chart=self.target_vars_in_chart)
            group_report_generator.draw_sheet()
        writer.close()


class GroupReportGenerator:
    def __init__(self, df, writer, sheet_name, variables, target_vars, target_vars_in_chart):
        self.df = df
        self.writer = writer
        self.sheet_name = sheet_name
        self.workbook = writer.book
        self.worksheet = self.workbook.add_worksheet(sheet_name)
        self.writer.sheets[sheet_name] = self.worksheet
        # 自变量列表
        self.variables = variables
        # 目标变量列表
        self.target_vars = target_vars
        # 需要图表展示的目标变量列表
        self.target_vars_in_chart = target_vars_in_chart
        # 画数据表行索引所在列，随着图表的增加更新
        self.row_ind = 0
        # 数据表中，索引所在列
        self.index_col_ind = 0
        # 因为列名需要增加的行数
        self.title_offset = 1
        # 因为索引需要增加的列数
        self.index_offset = 1
        # 图表占用的格子数
        self.chart_height = 15
        # 表格和图之间的空列数
        self.blank_col_between = 2
        # 不同变量报告之间的行数
        self.blank_row_between = 2

    def draw_sheet(self):
        for var_name in self.variables:
            target_calculator = URSDfCalculator(df=self.df, target_vars=self.target_vars,
                                                target_vars_calc_config=TARGET_VARS_CALC_CONFIG, var_name=var_name,
                                                numeric_var_quantile=NUMERIC_VAR_QUANTILE,
                                                enum_var_max_lines=ENUM_VAR_MAX_LINES,
                                                numeric_vars_as_enum=NUMERIC_VARS_AS_ENUM)
            urs_df = target_calculator.generate_urs_df()
            self.draw_var_table(urs_df=urs_df, var_name=var_name, row=self.row_ind)
            self.draw_var_chart(urs_df=urs_df, var_name=var_name, row=self.row_ind)
            self.row_ind += self.blank_row_between + max(self.chart_height, urs_df.shape[0])

    def draw_var_table(self, urs_df, var_name, row):
        urs_df.index.name = var_name
        urs_df.to_excel(self.writer, sheet_name=self.sheet_name, startrow=row, startcol=0)

    def draw_var_chart(self, urs_df, var_name, row):
        # 折现图画在表格右侧空一列处
        chart = self.workbook.add_chart({'type': 'line'})
        if not set(self.target_vars_in_chart).issubset(set(self.target_vars)):
            raise URSException(
                f'{set(self.target_vars_in_chart) - set(self.target_vars)} '
                f'does not contained in TARGET_VARS')
        # 每一个target_vars_in_chart中的变量绘制一条曲线
        for target_var in self.target_vars_in_chart:
            target_var_col_ind = self.target_vars.index(target_var) + self.index_offset
            chart.add_series({
                'categories': [self.sheet_name, row + self.title_offset, self.index_col_ind,
                               row + self.title_offset + urs_df.shape[0],
                               self.index_col_ind],
                'values': [self.sheet_name, row + self.title_offset, target_var_col_ind,
                           row + self.title_offset + urs_df.shape[0],
                           target_var_col_ind],
                'name': target_var
            })

        chart.set_x_axis({'name': var_name, 'position_axis': 'on_tick'})
        chart.set_y_axis({'name': 'value', 'major_gridlines': {'visible': True}})

        # Turn off chart legend. It is on by default in Excel.
        chart.set_legend({'position': 'bottom'})

        chart.set_size({'width': 960, 'height': 288})

        # Insert the chart into the worksheet.
        self.worksheet.insert_chart(row=row, col=urs_df.shape[1] + self.index_offset + self.blank_col_between,
                                    chart=chart)


class URSDfCalculator:
    def __init__(self, df, target_vars, target_vars_calc_config, var_name, numeric_var_quantile, enum_var_max_lines,
                 numeric_vars_as_enum):
        self.df = df
        # 目标变量列表
        self.target_vars = target_vars
        # 目标变量计算方式
        self.target_vars_calc_config = target_vars_calc_config
        # 自变量名
        self.var_name = var_name
        # 数值变量的分位点
        self.numeric_var_quantile = numeric_var_quantile
        # 枚举变量最大显示行数
        self.enum_var_max_lines = enum_var_max_lines
        # 数值变量强制作为枚举变量
        self.numeric_vars_as_enum = numeric_vars_as_enum

    def calc_target_vars(self, chosen_cond, calc_config):
        calc_way = calc_config.get('calc_way')
        orig_col = calc_config.get('orig_cols')
        if calc_way not in TargetVarsCalcWay:
            raise URSException(f'Unsupported calc way: {calc_way}')
        # 双目运算(赔付率， 相对赔付率）
        if calc_way in (TargetVarsCalcWay.RATIO, TargetVarsCalcWay.RATIO_REL):
            orig_col_left = orig_col[0]
            self._test_col_in_df(orig_col_left)
            orig_col_right = orig_col[1]
            self._test_col_in_df(orig_col_right)
            if calc_way == TargetVarsCalcWay.RATIO:
                return self.df[orig_col_left][chosen_cond].sum() / self.df[orig_col_right][chosen_cond].sum()
            else:
                return self.df[orig_col_left][chosen_cond].sum() / self.df[orig_col_right][chosen_cond].sum()

        # 单目运算 (count, sum, average)
        else:
            self._test_col_in_df(orig_col)
            return self.df[orig_col][chosen_cond].apply(calc_way.value)

    def generate_numeric_urs_df(self):
        self.df = self.df.sort_values(self.var_name, ascending=True)
        urs_index = pd.qcut(self.df[self.var_name], self.numeric_var_quantile, duplicates='drop').unique()
        urs_df = pd.DataFrame(index=urs_index, columns=self.target_vars)
        urs_df.index.name = self.var_name
        vars_rel_ratio = set()
        for row_cnt, ind in enumerate(urs_index):
            # 区分NAN值
            if type(ind) != float:
                chosen_cond = (self.df[self.var_name] > ind.left) & (self.df[self.var_name] <= ind.right)
            else:
                chosen_cond = self.df[self.var_name].isnull()
            for target_var, calc_config in self.target_vars_calc_config.items():
                if calc_config.get('calc_way') == TargetVarsCalcWay.RATIO_REL:
                    vars_rel_ratio.add(target_var)
                urs_df[target_var].iloc[row_cnt] = self.calc_target_vars(chosen_cond=chosen_cond,
                                                                         calc_config=calc_config)
        # rel变量需要重新计算一次相对值
        for var_rel in vars_rel_ratio:
            var_rel_tmp = var_rel + '_tmp'
            urs_df[var_rel_tmp] = urs_df[var_rel]
            urs_df[var_rel] = urs_df[var_rel_tmp] / (urs_df[var_rel_tmp].mean()) - 1
            urs_df.drop(var_rel_tmp, axis=1, inplace=True)
        return urs_df

    def generate_enum_urs_df(self):
        sorted_index = self.df[self.var_name].sort_values(ascending=True).unique()
        if len(sorted_index) > self.enum_var_max_lines:
            sorted_index = sorted_index[:self.enum_var_max_lines]
        urs_df = pd.DataFrame(index=sorted_index, columns=self.target_vars)
        urs_df.index.name = self.var_name
        vars_rel_ratio = set()
        for ind in sorted_index:
            if ind is np.nan:
                chosen_cond = self.df[self.var_name].isnull()
            else:
                chosen_cond = self.df[self.var_name] == ind
            for target_var, calc_config in self.target_vars_calc_config.items():
                if calc_config.get('calc_way') == TargetVarsCalcWay.RATIO_REL:
                    vars_rel_ratio.add(target_var)
                urs_df[target_var].loc[ind] = self.calc_target_vars(chosen_cond=chosen_cond, calc_config=calc_config)

        # rel变量需要重新计算一次相对值
        for var_rel in vars_rel_ratio:
            var_rel_tmp = var_rel + '_tmp'
            urs_df[var_rel_tmp] = urs_df[var_rel]
            urs_df[var_rel] = urs_df[var_rel_tmp] / (urs_df[var_rel_tmp].mean()) - 1
            urs_df.drop(var_rel_tmp, axis=1, inplace=True)
        return urs_df

    def _test_col_in_df(self, var_name):
        if var_name not in self.df.columns:
            raise URSException(f'{self.var_name} does not included in dataframe')

    def generate_urs_df(self):
        if set(self.target_vars) != set(self.target_vars_calc_config.keys()):
            raise URSException(f'TARGET_VARS does not match TARGET_VARS_CALC_CONFIG,'
                               f'details: {set(self.target_vars) ^ set(self.target_vars_calc_config.keys())}')
        if not self.var_name in self.df.columns:
            raise URSException(f'{self.var_name} does not included in dataframe')
        if self.df[self.var_name].dtype == object or self.var_name in self.numeric_vars_as_enum:
            return self.generate_enum_urs_df()
        elif self.df[self.var_name].dtype in [np.float64, np.int64]:
            return self.generate_numeric_urs_df()
        else:
            raise URSException(f'Unsupported type of {self.var_name}')


class URSException(Exception):
    pass


class ReportInfo:
    def __init__(self, data_source_type=DSType.PKL):
        if data_source_type == DSType.PKL:
            self.report_generator = ReportGenerator.create_generator_from_pickle()
        elif data_source_type == DSType.CSV:
            self.report_generator = ReportGenerator.create_generator_from_ascii(read_func=pd.read_csv)
        elif data_source_type == DSType.EXCEL:
            self.report_generator = ReportGenerator.create_generator_from_ascii(read_func=pd.read_excel)
        else:
            raise URSException(f'{data_source_type} does not support currently!')

    def to_excel(self):
        self.report_generator.to_excel()


if __name__ == '__main__':
    print('start to generate urs report')
    report_info = ReportInfo(data_source_type=DS_TYPE)
    report_info.to_excel()
    print('finished generating urs report')
