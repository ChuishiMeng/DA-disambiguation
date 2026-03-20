# AMBROSIA 论文笔记

**论文标题**: AMBROSIA: A Benchmark for Parsing Ambiguous Questions into Database Queries  
**作者**: Irina Saparina, Mirella Lapata (University of Edinburgh)  
**会议**: NeurIPS 2024 Datasets and Benchmarks Track  
**官网**: https://ambrosia-benchmark.github.io

---

## 1. 歧义分类方法

### 三种歧义类型

| 歧义类型 | 定义 | 示例问题 | 解释数量 |
|---------|------|---------|---------|
| **Scope Ambiguity**<br>(范围歧义) | 量词（如"each"、"every"、"all"）的指代范围不明确 | "What activities does each gym offer?" | 2种：<br>1. 集体解释：所有健身房共同提供的课程<br>2. 分布解释：每个健身房各自提供的课程 |
| **Attachment Ambiguity**<br>(附着歧义) | 修饰语或短语如何附着到句子其余部分不明确 | "Show the writers and editors on a work-for-hire." | 2种：<br>1. 高附着：编剧和编辑都是雇佣制<br>2. 低附着：只有编辑是雇佣制 |
| **Vagueness**<br>(模糊性) | 上下文导致不确定所指实体集合 | "Who issued CD Special?" | 2-3种：<br>1. 哪个银行发行的<br>2. 哪个分行发行的<br>3. 银行和分行都展示 |

### 关键区别

- **Scope & Attachment**: 属于**结构歧义**，句子有多个句法解析
- **Vagueness**: 通常只有**单一句法解析**，但因语义不精确可指向不同数据库实体

---

## 2. 基准数据集构建

### 数据集统计

| 指标 | 数值 |
|-----|------|
| 数据库数量 | 846 |
| 领域数量 | 16 |
| 平均每数据库表数 | 5.0 |
| 歧义问题总数 | 1,277 |
| - Scope歧义 | 501 |
| - Attachment歧义 | 362 |
| - Vagueness | 414 |
| 无歧义解释总数 | 2,965 |
| SQL查询总数 | 4,242 |

---

## 3. 实验结果

### 零样本实验 (Llama3-70B 最佳)

| 模型 | 歧义Recall | 无歧义Recall | AllFound |
|-----|-----------|-------------|----------|
| Llama3-70B | **30.7%** | 64.5% | **1.9%** |
| GPT-4o | 27.1% | 63.4% | 0.4% |
| CodeLlama-70B | 25.4% | - | 0.1% |

### 按歧义类型分解 (Llama3-70B)

| 歧义类型 | Recall | AllFound |
|---------|--------|----------|
| Scope | **41.5%** | 2.9% |
| Vague | 35.6% | 4.6% |
| Attachment | **12.7%** | 0.3% |

---

## 4. 关键发现

1. **模型难以识别歧义**: 所有模型在歧义问题上的 Recall 显著低于无歧义问题
2. **AllFound 极低**: 最佳模型仅 1.9% 的歧义问题能找到所有解释
3. **解释偏好偏差**: 模型倾向于特定类型的解释
4. **Attachment 最难**: 涉及复杂 SQL 操作
5. **少样本学习提升有限**: 增加示例有帮助但提升不显著

---

## 5. 与我们的三层框架对比

| AMBROSIA 分类 | 对应我们的框架 |
|--------------|---------------|
| Scope Ambiguity | **业务层**（语义解释） |
| Attachment Ambiguity | **业务层**（句法-语义映射） |
| Vagueness | **数据层**（实体映射歧义） |

**差异**：AMBROSIA 从语言学角度分类，我们从系统实现角度分类