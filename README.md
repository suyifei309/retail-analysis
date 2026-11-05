# retail-analysis：电商用户价值与流失分析

> **业务问题**：这家电商的高价值客户在流失吗？挽留券应该发给谁、发多少？
> **数据**：UCI [Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)（2009–2011，英国线上礼品电商，约 106 万条交易，CC BY 4.0）

## 环境

- conda 环境：`analyst`（Python 3.12 + pandas 3.x / sklearn / statsmodels / xgboost / shap / mlxtend）
- 启动：`conda activate analyst` 后在本目录运行 `code .`
- notebook 内核选择 `analyst` 环境的 Python

## 目录结构

| 目录 | 用途 |
|---|---|
| `data/raw/` | 原始数据，**只读不改** |
| `data/clean/` | 清洗后的数据（parquet） |
| `notebooks/` | 分析流水线：01 清洗 → 02 EDA → 03 建模 |
| `src/` | 可复用函数 |
| `reports/` | 图表与最终分析报告 |
| `docs/cleaning_rules.md` | 清洗规则表（每条规则：做了什么/为什么/影响多少行） |

## 分析计划

- [x] **W1** 数据下载（xlsx→parquet）+ 清洗，产出清洗规则表（1,067,371 行 → 交易表 1,007,913 + 退货表 19,494）
- [x] **W2** EDA + RFM 客群分层（5,878 客户，25% 客户贡献 69% GMV；新客同比 -55%；锁定 824 人流失风险客群）
- [x] **W3** 流失预警建模（时点切割防泄漏）：AUC 0.758 vs 基线 0.682；逻辑回归带 95% CI 追平 XGBoost；20% 预算覆盖 38% 真流失者；产出 churn_scores.parquet 投放名单
- [ ] **W4** 业务建议（3 发现 × 3 建议）+ A/B 验证方案（样本量计算）+ 最终报告

## 模型结论（03_model.ipynb）

- 2,788 位活跃客户（90 天流失率 38.2%），特征只用 2011-09-10 前数据，杜绝泄漏
- 逻辑回归（AUC 0.758，7/9 特征显著带 95% CI）≈ XGBoost（0.757）——关系近似线性时可解释性优先
- 预测最危险 20% 客户覆盖 38% 真流失者；客单价高/资历老的批发型客户是"假流失"陷阱（OR 0.61/0.60）
- 交付 `churn_scores.parquet`：10% 预算（278 人）名单 90 天历史销售额 £15.4 万

## 核心发现（02_eda.ipynb，图表见 reports/figures/）

1. **增长引擎熄火**：GMV 同比 +1.9% 几乎停滞，新客 3,387 → 1,508（-55%），2011-11 活跃中 88.5% 为老客
2. **价值高度集中**：25% 重要价值客户贡献 69% GMV（K-means 验证：8% 客户贡献 55%）；新客次月留存仅 21.2%
3. **挽留目标已锁定**：824 位流失风险客户（9% GMV ≈ £159 万）中位 373 天未回购 → W3 流失预警 + W4 A/B 挽留实验的对象

## 清洗后数据（01_clean.ipynb 产出）

- `data/clean/transactions.parquet`：1,007,913 行正常交易（占原始 94.4%），带 `has_customer` / `is_product` 标记
- `data/clean/returns.parquet`：19,494 行退货单
- 全部决策依据见 [docs/cleaning_rules.md](docs/cleaning_rules.md)

## 注意

- 原始 xlsx 不要提交进 git（见 .gitignore），仓库里只留下载脚本
- pandas 是 3.x，网上旧教程的个别 API 写法可能不适用
