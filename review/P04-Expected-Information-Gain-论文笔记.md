# Expected Information Gain 论文笔记

**标题**: Interactive Text-to-SQL via Expected Information Gain for Disambiguation  
**作者**: Luyu Qiu, Jianing Li, Chi Su, Lei Chen  
**机构**: HKUST, Hong Kong Polytechnic University  
**发表**: PVLDB 2025 (arXiv:2507.06467)

---

## 1. 期望信息增益（EIG）计算方法

### 核心公式

```
I(Xᵢ; Y) = H(Y) - H(Y|Xᵢ)
```

其中：
- `Y` = SQL 候选集合
- `Xᵢ` = 第 i 个决策变量（歧义点）
- `H(Y)` = 当前 SQL 分布的熵
- `H(Y|Xᵢ)` = 澄清 Xᵢ 后的条件熵

### 计算优化

**定理**: 最优澄清点可简化为：

```
X* = argmax P(Q* → Xᵢ) · H(Xᵢ)
           ↑              ↑
        相关性        歧义性
```

**计算复杂度**: 从 O(NM) 降至 O(N)

---

## 2. 澄清问题选择策略

### 算法流程

```
1. 检测决策变量集 X = {X₁, X₂, ..., Xₘ}
2. 计算 EIG(Xᵢ) = H(Y) - H(Y|Xᵢ)
3. 选择 x* = argmax EIG(Xᵢ)
4. 针对x 提出澄清问题，获取用户回答
5. 过滤候选: Y ← {Qᵢ ∈ Y : Qᵢ[X] = x*}
6. 更新概率分布，迭代直到收敛
```

### 决策变量类型

| 类型 | 示例 |
|------|------|
| 时间歧义 | "after 2020" → >'2020-12-31' vs ≥'2020-01-01' |
| 范围歧义 | "in sales" → 部门名 vs 职能 |
| Schema 歧义 | "List employees" → 所有列 vs 仅ID+姓名 |
| 列选择 | SELECT * vs SELECT id, name |
| 表选择 | Table1 vs Table2 |

---

## 3. 平衡"最小交互"和"准确消歧"

### 核心策略

EIG 天然平衡两个因素：
- **相关性 P(Q* → Xᵢ)**: 确保问题"值得问"
- **歧义性 H(Xᵢ)**: 确保问题"有信息量"

### 终止条件

1. 最高候选置信度超过阈值 τ
2. 所有决策变量已解决

---

## 4. 实验结果

### Spider 歧义子集

| 策略 | Exact Match | Execution |
|------|-------------|-----------|
| Random | 19.0% | 70.1% |
| Max Probability | 30.6% | 72.1% |
| **EIG (Ours)** | **38.3%** | **76.6%** |

### Spider 2.0 提升

| 方法 | w/o EIG | w/ EIG | 提升 |
|------|---------|--------|------|
| DIN-SQL | 1.46% | 4.41% | +202% |
| DAIL-SQL | 5.68% | 8.56% | +51% |
| Spider-Agent | 13.71% | 17.12% | +25% |

---

## 5. 与其他方法对比

| 方法 | 策略 | 局限性 |
|------|------|--------|
| PIIA / Dial-SQL | 固定顺序提问 | 缺乏原则性策略 |
| DIY / NaLIR | 用户主动修正 | 被动交互 |
| Wang et al. | 仅处理列歧义 | 范围有限 |
| **EIG** | **基于信息论** | **全局最优，模型无关** |

---

## 6. 核心贡献

1. **形式化**: 将 Text-to-SQL 建模为交互式、不确定性驱动的推理
2. **EIG 策略**: 基于互信息的原则性交互策略
3. **效率优化**: 计算复杂度从 O(NM) 降至 O(N)
4. **实证验证**: 在多个数据集上显著超越基线