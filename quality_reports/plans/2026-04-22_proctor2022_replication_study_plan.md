# Proctor2022 Replication Study Plan

日期：2026-04-22

## 任务目标

梳理 `C:\YangSu\00_Project\CA_mechanism\code\proctor2022_replication` 的论文复现代码，明确其分析是如何展开的、核心识别与函数逼近原理是什么、图表是如何由模型对象生成的，并据此说明哪些结构可以迁移到当前 `regression_SR` project。

## 检查范围

- 说明文件：`Readme_Proctor2022_NatFood.rtf`
- 公共函数：`Code/analysis_helper_functions.R`
- 主图脚本：`Code/Fig2.R`、`Code/Fig3_FigED6.R`
- 必要时补充读取其他图表脚本与 `Data/` 目录文件名

## 输出要求

- 用中文说明代码展开顺序
- 用精确表述解释核心估计原理
- 将原项目做法映射到本 project 的 `grid_id × year` 面板框架
- 标注可直接复用、需改写、不可照搬三类部分

## 验证

- 核对说明文件、主脚本、公共函数三类来源是否一致
- 交叉检查主脚本中的模型设定、辅助函数中的实现细节、结果输出路径是否一致
