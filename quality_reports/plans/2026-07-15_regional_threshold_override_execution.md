# 地区异质温度阈值继续执行设计

## Material Passport

- Canonical ID：`regional-threshold-sr-override-v1`
- Parent evidence：`regional-threshold-sr-v1`（历史 `STOP_DATA_SUPPORT_GATE` 报告保持不变）
- 工作流：Academic Research Suite / experiment-agent，`run` + `validate`
- 用户授权：2026-07-15“继续执行，不考虑这个门槛”
- 执行边界：取消五区各自80%阈值覆盖率的阻断效力，不取消输入真实性、键唯一性、时间轴、代码测试、complete-case、可识别性和结果完整性检查

## 研究对象与样本

本轮只使用官方连续阈值原始像元有效且位于五个命名产区的V3 grid-year，不插值、不外推、不以固定32°C回填阈值缺失。确认性样本因此是外生阈值complete-case，而不是原66,396行pre-EDD样本；西南69.8408%的原始覆盖率必须在所有结果中披露。V3结果变量为`ln_yield`，SR变量为`ca`，控制变量为`gdd_10_29`、`pr_sum`及`pr_sum^2`。固定效应为grid FE与由`province`和`year`重新生成的province×year FE。

## 暴露定义

外生阈值由用户提供且哈希与Zenodo记录一致的`maize.tif`按格网中心所在0.5°PixelIsArea像元映射，阈值保持连续。温度输入是项目已有的逐日Tmax，不是公开`CalExposure.m`所需的逐小时温度，因此所有变量明确命名为`daily approximation`：

\[
HDD^{daily}_{itw}=\sum_{d\in w}\max(Tmax_{itd}-\tau_i,0),\qquad
Days^{daily}_{itw}=\sum_{d\in w}1(Tmax_{itd}\ge\tau_i).
\]

主暴露为`threshold_hdd_cday_daily`，`threshold_exceedance_days_daily`作共同描述；固定32°C使用相同逐日定义作预设对照。不存在28—40°C的内部搜索。

三个固定窗口为：扩展V3—成熟窗口`[V3-30, MA]`；V3—HE窗口`[V3, HE)`；HE—MA窗口`[HE, MA]`。后两个窗口不重叠，MA日纳入HE—MA。每一grid-window要求Tmax全日完整，否则该暴露置为缺失。

## SM状态与通道

GLEAM SMrz使用与温度相同的0.1°逐日格网。每个窗口开始前14日至前1日为antecedent state；窗口内计算SMrz均值、最低值、均值相对前置状态的变化以及最低值相对前置状态的drawdown。SM变量不加入主产量方程后再称为因果中介。

状态模型在主扩展窗口内估计五区`CA×HDD×antecedent SM`完全低阶交互，并分别报告各区antecedent SM P25/P75时的SR条件损害差异。通道模型以`SM mean - antecedent`和`SM min - antecedent`为结果，估计五区`CA×HDD`交互；这些结果只称为通道一致的条件相关结构。

## 模型与估计量

主产量模型为五区合并模型。每个产区分别生成居中的HDD、CA及其乘积，保留五区全部低阶项；区域水平项由grid FE吸收。共同CA端点为外生阈值complete-case样本的P25/P75，每区HDD端点为该区P50/P90。主要估计量为：

\[
\Delta Buffer_z=\hat\beta_{CA\times HDD,z}(CA_{75}-CA_{25})(HDD_{90,z}-HDD_{50,z}).
\]

正值表示高SR下P50至P90高温暴露对应的条件产量损害较低SR更小。区间先使用grid聚类协方差；2°空间块wild bootstrap未完成前不得把区间写成计划中的最终主推断。LOYO四折只报告交互方向稳定性，不称为交叉验证或外部验证。

## 计算性检查

必须满足：输入文件存在且哈希登记；V3的`grid_id year`唯一；逐日温度和GLEAM日期轴与目标年份逐日连续；V3的`lat_idx/lon_idx`与两个NetCDF坐标一致；窗口长度和边界通过人工序列单元测试；外生阈值无插补；所有五区均输出支持和结果；模型设计矩阵满列秩且FE去除收敛。只有输入缺失、日期错误、实现错误或模型不可识别可以停止计算，覆盖率和结果方向不再阻断。

## 输出位置

代码只新增`regional_threshold_daily_*`文件及其测试；所有行级派生数据、模型对象、日志和二进制图表写入新的`temp/2026-07-15_regional_threshold_daily_override_v1/`。本执行代理不修改公共谱系、版本索引或历史报告。
