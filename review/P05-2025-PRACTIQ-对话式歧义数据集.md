# PRACTIQ: A Practical Conversational Text-to-SQL Dataset 论文笔记

**标题**: PRACTIQ: A Practical Conversational text-to-SQL dataset with Ambiguous and Unanswerable Queries  
**作者**: Mingwen Dong, Nischal Ashok Kumar 等 (UMass Amherst + Amazon AWS)  
**发表**: NAACL 2025  
**代码**: github.com/amazon-science/conversational-ambiguous-unanswerable-text2sql  

---

## 1. 核心贡献

- 识别并定义了 **4 种歧义** + **4 种无法回答** 问题类别
- 构建了包含 **2800 个对话**的实用数据集 PRACTIQ
- 对话包含 4 轮：初始问题 → 澄清请求 → 用户澄清 → SQL + 解释

---

## 2. 歧义与无法回答分类

### 歧义类别（4种）

| 类别 | 定义 | 示例 |
|------|------|------|
| **Ambiguous SELECT Column** | SELECT 列有多个可能映射 | "maximum capacity" → standing vs seating capacity |
| **Ambiguous WHERE Columns** | WHERE 条件可映射到多列 | property_type = 5 → property_type_code vs property_type_version |
| **Ambiguous Values Within Column** | 列内有多个值匹配 | "Chemistry teacher" → Organic Chemistry vs Physical Chemistry |
| **Ambiguous Filter Criteria** | 过滤条件定义模糊 | "underage" → 具体年龄阈值未定义 |

### 无法回答类别（4种）

| 类别 | 定义 | 示例 |
|------|------|------|
| **Nonexistent SELECT Column** | 查询列不存在 | "nickname" 不在表中 |
| **Nonexistent WHERE Column** | 过滤列不存在 | "tin mining" 没有对应列 |
| **Nonexistent Filter Value** | 过滤值不存在 | "New York Yankees" 不在团队表中 |
| **Unsupported Join** | 表之间无法 JOIN | 学生表和图书表无外键关联 |

---

## 3. 数据生成方法

三阶段流程：
1. **SQL 解析 + 数据库修改**: 修改 Schema 使问题变得歧义/无法回答
2. **反向生成**: 先改 SQL → LLM 生成澄清对话
3. **对话精炼**: 完善自然语言流畅度和一致性

特殊处理：对 Ambiguous SELECT/WHERE 类别，除了澄清问题外，还生成"**helpful SQL**"直接返回所有歧义列结果。

---

## 4. 实验发现

- 当前 SOTA LLM 在歧义和无法回答问题上表现不佳
- 需要两步流程：先分类问题类别，再生成澄清 SQL
- **无法回答问题**比歧义问题更难处理

---

## 5. 与我们研究的关联

| 维度 | 启示 |
|------|------|
| **歧义分类** | 比 AMBROSIA 更细粒度（8类 vs 3类），更贴近实际场景 |
| **无法回答** | 首次系统化处理"问题不可回答"场景 |
| **对话流程** | 4 轮对话设计可直接参考 |
| **数据构建** | 通过修改 Schema 生成歧义的方法可复用 |

---

## 6. 局限性

- 数据基于 Spider 修改生成，非真实用户数据
- 仅覆盖单数据库场景
- 未涉及用户画像/个性化
