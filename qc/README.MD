# 数据质量(qc)报告使用文档

程序目前支持的数据集格式为csv和pickle（从pandas中调用to_pickle方法生成）

生成的[示例qc报告文档](./dataQualityReports/示例QC报告.html)

## 运行环境
python版本: 3.0

安装qc文件夹同级目录下[requirements.txt](../requirements.txt)中的依赖

```shell
pip install -r requirements.txt
```


## 配置说明
配置内容位于[format_config.py](./format_config.py)中

分为默认配置、通用配置与专用配置

默认配置: 一般不需要进行修改（在对生成的报告格式有特殊要求时需要）

通用配置: 更换数据集来源文件时需要重新配置的部分

专用配置: 根据数据集文件的类型（csv/pickle)需要额外做的配置项

具体的配置对应的说明在format_config.py中有详细的说明

## 使用说明

根据数据集填写好配置文件后，运行[report_generator.py](./report_generator.py)

```shell
python report_generator.py

```

生成的文件会保存在[dataQualityReports](./dataQualityReports)目录下
