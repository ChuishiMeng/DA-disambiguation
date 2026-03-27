# P14 - Towards Knowledge-Intensive Text-to-SQL Semantic Parsing with Formulaic Knowledge

> 论文笔记 | 2026-03-27

---

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| **标题** | Towards Knowledge-Intensive Text-to-SQL Semantic Parsing with Formulaic Knowledge |
| **作者** | Longxu Dou, Yan Gao, etc. (NUS) |
| **发表** | EMNLP 2022 |
| **链接** | https://aclanthology.org/2022.emnlp-main.350/ |
| **PDF** | https://www.comp.nus.edu.sg/~kanmy/papers/formulaic-knowledge-emnlp22.pdf |

---

## 🎯 问题定义

### 知识密集型 Text-to-SQL

**核心场景**：领域专家提出的问题需要**领域知识**才能正确解析为 SQL

**典型例子**：
```
问题："中国2020年人口密度是多少？"

需要的知识：
- 人口密度 = 总人口 / 土地面积
- 中国2020年人口数据
- 中国土地面积数据

SQL 需要的计算：
SELECT total_population / land_area FROM china_stats WHERE year = 2020
```

### 与传统 Text-to-SQL 的区别

| 维度 | 传统 Text-to-SQL | 知识密集型 Text-to-SQL |
|------|-----------------|----------------------|
| 问题来源 | 普通用户 | 领域专家 |
| 知识需求 | 仅 Schema | Schema + 领域知识 |
| 计算复杂度 | 简单查询 | 复杂计算逻辑 |
| 歧义类型 | Schema 歧义 | 知识歧义 |

---

## 📊 数据集：KnowSQL

### 基于 DuSQL 扩展

- **DuSQL**：大规模中文跨领域 Text-to-SQL 数据集
  - 200 个数据库，813 张表
  - 23,797 个问题/SQL 对
  - 包含数学计算问题

- **KnowSQL**：在 DuSQL 基础上扩展
  - Train/Dev 基于 DuSQL
  - 新增 Finance（金融）等领域测试集
  - 标注了所需的公式化知识

### 数据集统计

| 划分 | 用途 | 特点 |
|------|------|------|
| Train/Dev | 训练/验证 | 基于 DuSQL |
| Finance | 测试 | 金融领域知识 |

---

## 🔧 方法：ReGrouP 框架

### 三阶段管道

```
问题 + Schema
     ↓
[1] Retrieve：从知识库检索相关公式化知识
     ↓
[2] Ground：将抽象概念接地到具体 Schema 元素
     ↓
[3] Parse：使用接地后的知识解析 SQL
     ↓
SQL 查询
```

### 阶段详解

#### 1. Retrieve（检索）

- 使用 **Dense Passage Retriever (DPR)**
- 计算问题与知识库中条目的相似度
- 检索最相关的公式化知识

#### 2. Ground（接地）

- 将抽象概念映射到具体 Schema 元素
- 例如：
  - "人口密度" → `total_population / land_area`
  - "中国2020年" → `WHERE year = 2020 AND country = 'China'`

#### 3. Parse（解析）

- 使用 Erasing-Then-Awakening 模型
- 输入：问题 + Schema + 接地后的知识
- 输出：SQL 查询

---

## 📚 公式化知识类型

论文定义了**三种公式化知识**：

### 1. 计算型（Calculation）

- **定义**：需要数学计算的知识
- **例子**：人口密度 = 人口 / 面积
- **SQL 表达**：`SELECT population / area FROM table`

### 2. 领域特定型（Domain-Specific）

- **定义**：特定领域的业务规则
- **例子**：金融领域的"ROI"计算公式
- **特点**：需要行业专业知识

### 3. 概念型（Concept）

- **定义**：抽象概念到具体字段的映射
- **例子**："用户活跃度" → 登录次数 / 天数
- **作用**：连接用户表达与数据库结构

---

## 📈 实验结果

### 主要结果

| 模型 | Dev | Finance | Average |
|------|-----|---------|---------|
| Vanilla Parser | - | - | 基线 |
| + ReGrouP (Oracle) | - | - | 显著提升 |
| + ReGrouP (Retrieved) | - | - | **+28.2%** |

### 关键发现

1. **知识注入效果显著**：28.2% 的整体提升
2. **知识可扩展**：无需重新训练即可添加新知识
3. **检索质量关键**：Oracle（完美检索）vs Retrieved 的差距

---

## 💡 对 DA-disambiguation 项目的启示

### 1. 业务层歧义

**公式化知识 → 业务知识图谱**

| ReGrouP | 我们的框架 |
|---------|-----------|
| 公式化知识库 | 业务知识图谱 |
| 计算型知识 | 业务规则 |
| 领域特定知识 | 行业知识 |

### 2. 知识歧义消解

**ReGrouP 解决的是"缺少知识"的问题**

我们的框架需要解决：
- 知识存在但有多种解释 → 歧义消解
- 知识需要与用户意图匹配 → 用户画像

### 3. 三层协同

```
用户层：用户意图 → 哪种知识？
    ↓
业务层：业务规则 → 知识的正确形式
    ↓
数据层：Schema → 知识的落地实现
```

---

## 🔗 与其他文献的关系

### 与 P13 (Knowledge Base Construction) 的关系

| P14 (2022) | P13 (2025) |
|-----------|-----------|
| 公式化知识 | 通用知识库 |
| 手动标注 | 自动构建 |
| 领域固定 | 跨领域复用 |

**演进路径**：P14 提出概念 → P13 实现自动化

### 与 P01 (Disambiguate First) 的关系

- **P01**：先生成解释，再解析 SQL
- **P14**：先检索知识，再解析 SQL
- **共同点**：两阶段解耦

---

## 📝 关键引用

```bibtex
@inproceedings{dou2022towards,
  title={Towards Knowledge-Intensive Text-to-SQL Semantic Parsing with Formulaic Knowledge},
  author={Dou, Longxu and Gao, Yan and others},
  booktitle={EMNLP},
  year={2022}
}
```

---

## ✅ 总结

### 核心贡献

1. **定义了知识密集型 Text-to-SQL 问题**
2. **提出公式化知识表示**
3. **设计 ReGrouP 框架实现知识注入**
4. **构建 KnowSQL 数据集**

### 局限性

1. 知识库需手动构建
2. 检索质量依赖 DPR
3. 未考虑用户意图歧义

### 对我们的价值

- **业务层知识表示**：公式化知识 → 业务规则
- **知识注入方法**：检索 → 接地 → 解析
- **数据集参考**：KnowSQL 的标注方法

---

*笔记整理：科研小新 | 2026-03-27*