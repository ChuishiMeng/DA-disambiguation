# Odin: A NL2SQL Recommender to Handle Schema Ambiguity 论文笔记

**标题**: Odin: A NL2SQL Recommender to Handle Schema Ambiguity  
**作者**: Kapil Vaidya, Abishek Sankararaman, Jialin Ding 等 (AWS)  
**发表**: arXiv 2505.19302 (2025-05)  
**来源**: Amazon Web Services + MIT

---

## 1. 核心贡献

- 提出 **Generate-Select-Personalize** 三组件框架处理 Schema 歧义
- **Generator**: 基于 Schema Masking 的多样性 SQL 生成（vs 高温采样）
- **Selector**: 基于 Conformal Prediction 的候选过滤，提供统计覆盖保证
- **Personalizer**: 从用户反馈学习偏好，生成文本提示指导后续生成
- 在 AmbiQT 基准上，正确 SQL 出现概率提升 **1.5-2×**，结果集缩小 **2-2.5×**

---

## 2. 问题定义

传统 NL2SQL 输出单一 SQL，但企业环境中 Schema 歧义普遍：
- **表歧义**: curr_dept vs dept_2022
- **列歧义**: gross_sales vs net_sales  
- **结构歧义**: 不同解释导致完全不同的 JOIN 结构

优化目标：**最大化正确 SQL 包含概率，限制结果集大小 ≤ K**

```
max AvgAcc(W), subject to AvgResultSize(W) ≤ K
```

---

## 3. 技术架构

### 3.1 Generator: Schema Masking 策略

**问题**: 高温采样仅产生表面变化（别名、子查询改写），不改变执行结果。

**解决方案**: 逐步移除已用 Schema 元素，强制 LLM 探索替代路径。

```
完整 Schema → 生成 SQL₁ → 移除 SQL₁ 用到的列 → 掩码 Schema → 生成 SQL₂ → ...
```

**优化**:
- **重复检测**: 记录已探索的掩码 Schema，避免重复
- **贪心搜索**: 优先队列按 Schema 相关性评分排序
- **评分函数**: SBERT 相似度 × 最小实体覆盖度

### 3.2 Selector: Conformal Prediction

- 为候选 SQL 打分（LLM-based 或 SBERT-based）
- **LLM 打分**: Prompt "Does SQL answer the question? A.Yes B.No"，取 B 的 logit 概率
- **SBERT 打分**: 实体-SQL列匹配度，取最小相似度
- **阈值选择**: 基于 Calibration Set 的分位数，保证覆盖概率 ≥ 1-α

### 3.3 Personalizer: 偏好学习

- 用户选择正确 SQL → 提取 **Schema Linking 映射**
- 生成文本提示："When referring to total sales, the user prefers gross_sales over net_sales"
- **Generator 集成**: 提示注入 LLM context
- **SBERT 微调**: Triplet loss 拉近偏好实体、推远非偏好实体
- 支持 **偏好漂移**（滑动窗口/衰减函数）

---

## 4. 实验结果

### AmbiQT + Mod-AmbiQT 基准

| 方法 | Join Acc | Table Acc | Column Acc | 结果集大小 |
|------|----------|-----------|------------|-----------|
| Sampling (K=10) | 15.5% | 30.0% | 52.0% | 10 |
| Forced Diversity | 33.2% | 38.0% | 58.8% | 10 |
| **Odin** | **71.6%** | **50.3%** | **73.6%** | 4.9/4.2/3.9 |

### Personalizer 效果（K=1）
- Join 歧义提升 **+30%**，Column 歧义提升 **+30%**
- 说明用户偏好学习即使在单次生成中也显著有效

### Generator 对比
- Schema Masking 在 BothInTopK 上比 Logical Beam 高 **1.2-1.9×**
- 证明 Schema Masking 产生真正多样的 SQL，而非表面变化

---

## 5. 与我们研究的关联

| 维度 | 启示 |
|------|------|
| **Schema 歧义** | 最系统化的 Schema 歧义处理方案，直接对应我们的"数据层歧义" |
| **推荐而非单答案** | 面对歧义时提供候选集而非猜测，减少错误 |
| **用户偏好学习** | Personalizer 直接对应我们的"用户层"消歧需求 |
| **Conformal Prediction** | 提供统计保证的过滤方法，可作为我们的 Selector 参考 |
| **文本提示** | 偏好学习通过文本提示而非模型重训练，更轻量 |

---

## 6. 局限性

1. 仅处理 Schema 歧义（表/列歧义），不处理语言歧义（如 P02 的 Scope/Attachment）
2. 需要用户显式反馈（选择正确 SQL），冷启动问题
3. Mod-AmbiQT 是人工构建的基准，非真实场景
4. 多轮对话支持有限
