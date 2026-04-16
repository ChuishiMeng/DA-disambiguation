#!/usr/bin/env python3
"""
Pilot Study Phase 3: 构造跨层耦合测试案例
基于 P1 三层框架，设计针对性歧义案例
"""

import json
import os

OUTPUT_DIR = "~/agent-work/research/DA-disambiguation/pilot-study"

# 基于 P1 定义的三层歧义框架构造典型案例
TEST_CASES = [
    # ========== 类型1: 用户层 + 业务层耦合 ==========
    {
        "id": "CUST_001",
        "type": "用户层+业务层耦合",
        "question": "我的优质用户销售额是多少？",
        "ambiguity_analysis": {
            "user_layer": {
                "指代省略": "我的 → 指代哪个部门/区域？",
                "角色视角": "用户可能是销售代表（看个人）或总监（看全局）"
            },
            "business_layer": {
                "概念歧义": "优质用户 → 存款达标？理财达标？按时还款？",
                "逻辑歧义": "销售额 → 销售金额？销售数量？含税/不含税？"
            },
            "cross_layer_coupling": "角色视角决定'优质用户'的定义：总监看全公司标准，代表看个人客户标准"
            },
        "expected_sql_variants": [
            "销售代表视角：SELECT SUM(amount) FROM sales WHERE user_id = {current_user} AND customer_level = 'VIP'",
            "总监视角：SELECT SUM(amount) FROM sales WHERE department = {user_dept} AND customer_level = 'PREMIUM'"
        ],
        "difficulty": "challenging"
    },
    
    # ========== 类型2: 业务层 + 数据层耦合 ==========
    {
        "id": "CUST_002",
        "type": "业务层+数据层耦合",
        "question": "上个月复购率最高的产品类别",
        "ambiguity_analysis": {
            "user_layer": {
                "时间模糊": "上个月 → 自然月？财务月？滚动30天？"
            },
            "business_layer": {
                "逻辑歧义": "复购率 → 用户复购率？订单复购率？商品复购率？",
                "概念歧义": "产品类别 → SKU级？品类级？品牌级？"
            },
            "data_layer": {
                "表歧义": "产品类别 → products.category？categories.name？",
                "路径歧义": "JOIN路径：订单→商品→类别 或 用户→购买记录→商品→类别"
            },
            "cross_layer_coupling": "复购率定义决定JOIN路径：用户复购率需要用户维度聚合，商品复购率需要商品维度聚合"
        },
        "expected_sql_variants": [
            "用户复购率：SELECT c.name, COUNT(DISTINCT u.user_id) as repeat_users FROM orders o JOIN users u JOIN products p JOIN categories c ...",
            "商品复购率：SELECT c.name, COUNT(o.order_id) as repeat_orders FROM orders o JOIN products p JOIN categories c ..."
        ],
        "difficulty": "challenging"
    },
    
    # ========== 类型3: 用户层 + 数据层耦合 ==========
    {
        "id": "CUST_003",
        "type": "用户层+数据层耦合",
        "question": "最近它的交易金额",
        "ambiguity_analysis": {
            "user_layer": {
                "指代省略": "它 → 指代哪个实体？客户？商品？订单？",
                "时间模糊": "最近 → 最近7天？30天？最近一次？"
            },
            "data_layer": {
                "表歧义": "交易 → transactions表？orders表？payments表？",
                "字段歧义": "金额 → amount？total_price？paid_amount？"
            },
            "cross_layer_coupling": "'它'的指代决定查询的表：如果'它'=客户→查询客户关联订单，如果'它'=商品→查询商品销售记录"
        },
        "expected_sql_variants": [
            "客户视角：SELECT SUM(o.amount) FROM orders o WHERE o.customer_id = {target_customer} AND o.date >= DATE_SUB(NOW(), INTERVAL 30 DAY)",
            "商品视角：SELECT SUM(p.amount) FROM products p WHERE p.product_id = {target_product} AND p.sale_date >= ..."
        ],
        "difficulty": "moderate"
    },
    
    # ========== 类型4: 三层全耦合（最复杂）==========
    {
        "id": "CUST_004",
        "type": "三层全耦合",
        "question": "我们部门优质客户上季度的平均购买频次",
        "ambiguity_analysis": {
            "user_layer": {
                "指代省略": "我们部门 → 用户所在哪个部门？",
                "时间模糊": "上季度 → 自然季度？财务季度？"
            },
            "business_layer": {
                "概念歧义": "优质客户 → 定义标准多种",
                "逻辑歧义": "平均购买频次 → 购买次数/客户数？购买次数/时间段？",
                "规则歧义": "购买频次计算规则 → 按天？按周？按月？"
            },
            "data_layer": {
                "表歧义": "购买 → orders？purchases？transactions？",
                "路径歧义": "部门→客户→订单 的JOIN路径不唯一"
            },
            "cross_layer_coupling": "三层歧义相互约束：部门确定→客户范围确定→优质标准确定→计算逻辑确定"
        },
        "expected_sql_variants": [
            "解释1：SELECT AVG(count_orders) FROM (SELECT customer_id, COUNT(*) as count_orders FROM orders WHERE dept = {user_dept} AND quarter = 'Q3' AND customer_level = 'VIP' GROUP BY customer_id)",
            "解释2：SELECT COUNT(*) / COUNT(DISTINCT customer_id) FROM orders WHERE dept = {user_dept} AND quarter = 'Q3' AND customer_score > 80"
        ],
        "difficulty": "challenging"
    },
    
    # ========== 类型5: 简单歧义（对照组）==========
    {
        "id": "CUST_005",
        "type": "单层歧义（对照组）",
        "question": "销售额前10的客户",
        "ambiguity_analysis": {
            "user_layer": {},
            "business_layer": {
                "逻辑歧义": "销售额 → 销售金额？销售数量？"
            },
            "data_layer": {},
            "cross_layer_coupling": "无跨层耦合，单层消歧即可"
        },
        "expected_sql_variants": [
            "SELECT customer_id, SUM(amount) as total_sales FROM orders GROUP BY customer_id ORDER BY total_sales DESC LIMIT 10",
            "SELECT customer_id, COUNT(*) as sales_count FROM orders GROUP BY customer_id ORDER BY sales_count DESC LIMIT 10"
        ],
        "difficulty": "simple"
    },
    
    # ========== 类型6: 高频歧义组合（基于Phase2发现）==========
    {
        "id": "CUST_006",
        "type": "高频歧义组合",
        "question": "按地区统计优质客户的平均消费金额",
        "ambiguity_analysis": {
            "user_layer": {
                "维度约定": "按地区 → 省级？市级？区域级？"
            },
            "business_layer": {
                "概念歧义": "优质客户 → 定义标准",
                "逻辑歧义": "平均消费金额 → 总金额/客户数？单次平均？"
            },
            "data_layer": {
                "路径歧义": "地区→客户→消费 的JOIN路径"
            },
            "cross_layer_coupling": "维度约定影响聚合粒度，概念歧义影响筛选条件"
        },
        "expected_sql_variants": [
            "省级聚合：SELECT province, AVG(total_amount) FROM customers c JOIN orders o WHERE c.level = 'VIP' GROUP BY province",
            "市级聚合：SELECT city, SUM(amount)/COUNT(DISTINCT customer_id) FROM customers c JOIN orders o WHERE c.score > 70 GROUP BY city"
        ],
        "difficulty": "moderate"
    }
]

def main():
    print("=" * 60)
    print("Phase 3: 构造跨层耦合测试案例")
    print("=" * 60)
    
    print(f"\n构造案例数: {len(TEST_CASES)}")
    
    # 类型分布
    from collections import Counter
    type_dist = Counter(tc["type"] for tc in TEST_CASES)
    print("\n案例类型分布:")
    for t, c in type_dist.most_common():
        print(f"  {t}: {c}")
    
    # 难度分布
    diff_dist = Counter(tc["difficulty"] for tc in TEST_CASES)
    print("\n难度分布:")
    for d, c in diff_dist.most_common():
        print(f"  {d}: {c}")
    
    # 详细展示每个案例
    print("\n" + "=" * 60)
    print("案例详情")
    print("=" * 60)
    
    for tc in TEST_CASES:
        print(f"\n### [{tc['id']}] [{tc['type']}] [{tc['difficulty']}] ###")
        print(f"问题: {tc['question']}")
        print(f"\n歧义分析:")
        for layer, analysis in tc['ambiguity_analysis'].items():
            if layer == "cross_layer_coupling":
                print(f"  跨层耦合: {analysis}")
            elif isinstance(analysis, dict) and analysis:
                print(f"  {layer}:")
                for k, v in analysis.items():
                    print(f"    - {k}: {v}")
        
        print(f"\n预期SQL变体数: {len(tc['expected_sql_variants'])}")
    
    # 保存案例
    output_path = os.path.expanduser(f"{OUTPUT_DIR}/constructed_test_cases.json")
    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": "2026-04-15",
            "description": "基于P1三层框架构造的跨层耦合测试案例",
            "total_cases": len(TEST_CASES),
            "cases": TEST_CASES
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n案例已保存: {output_path}")
    
    # 总结
    print("\n" + "=" * 60)
    print("Phase 3 总结")
    print("=" * 60)
    print("\n构造案例覆盖:")
    print("✅ 用户层+业务层耦合")
    print("✅ 业务层+数据层耦合")
    print("✅ 用户层+数据层耦合")
    print("✅ 三层全耦合（最复杂）")
    print("✅ 单层歧义（对照组）")
    print("✅ 高频歧义组合（基于Phase2发现）")
    print("\n这些案例可用于:")
    print("  1. 测试LLM对跨层歧义的处理能力")
    print("  2. 验证三层协同框架的必要性")
    print("  3. 设计消歧策略的实验基准")

if __name__ == "__main__":
    main()