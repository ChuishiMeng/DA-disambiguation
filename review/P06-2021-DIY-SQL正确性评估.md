# P06 - DIY: Assessing Correctness of NL2SQL Systems 论文笔记

**标题**: DIY: Assessing the Correctness of Natural Language to SQL Systems  
**发表**: IUI 2021  
**作者**: Narechania, Fourney 等 (Microsoft)  

---

## 1. 核心贡献

- 系统分析了 NL 歧义对 SQL 生成正确性的影响
- 提出面向终端用户的 SQL 正确性评估方法
- 发现 **用户对歧义 SQL 的识别能力有限**

---

## 2. 关键发现

| 发现 | 说明 |
|------|------|
| 歧义普遍存在 | 即使简单的自然语言问题也可能映射到多个 SQL |
| 用户判断困难 | 非技术用户难以判断生成的 SQL 是否正确 |
| 表面正确性陷阱 | 语法正确但语义错误的 SQL 最难被用户发现 |

---

## 3. 与我们研究的关联

- **验证了歧义消解的用户侧必要性**：即使系统生成了 SQL，用户也无法判断正确性
- 支持我们"在生成 SQL 前消歧"的方向
- 用户评估能力有限 → 强调自动化消歧的重要性
