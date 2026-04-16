#!/usr/bin/env python3
"""
Pilot Study Phase 1B: 手动歧义分析
基于 P1 三层框架，人工分析典型查询的歧义类型
"""

import json
import os

TEST_DATA = "~/agent-work/research/DA-disambiguation/pilot-study/test_cases_100.json"
OUTPUT_DIR = "~/agent-work/research/DA-disambiguation/pilot-study"

# 歧义信号关键词（基于 P1 定义）
USER_LAYER_SIGNALS = {
    "指代省略": ["its", "their", "this", "that", "the"],
    "时间模糊": ["recent", "latest", "current", "last", "previous", "annual"],
    "角色视角": ["my", "our", "personal"],
    "偏好差异": ["best", "worst", "favorite", "preferred"]
}

BUSINESS_LAYER_SIGNALS = {
    "概念歧义": ["customer", "user", "client", "member",  # 多定义概念
                "segment", "category", "type"],
    "逻辑歧义": ["ratio", "average", "percentage", "difference", 
                "rate", "growth", "increase", "decrease"],
    "规则歧义": ["annual", "monthly", "quarterly", "yearly"],
    "维度约定": ["by", "per", "for", "in", "within"]
}

DATA_LAYER_SIGNALS = {
    "表歧义": ["consumption", "payment", "transaction", "order", "sales"],
    "字段歧义": ["amount", "value", "price", "cost", "total"],
    "路径歧义": ["join", "inner", "left", "between", "and"]
}

def detect_ambiguity(question, ground_truth_sql):
    """检测歧义类型"""
    detected = {
        "user_layer": [],
        "business_layer": [],
        "data_layer": [],
        "cross_layer": False
    }
    
    # 用户层检测
    for type_name, keywords in USER_LAYER_SIGNALS.items():
        for kw in keywords:
            if kw.lower() in question.lower():
                detected["user_layer"].append(type_name)
                break
    
    # 业务层检测
    for type_name, keywords in BUSINESS_LAYER_SIGNALS.items():
        for kw in keywords:
            if kw.lower() in question.lower():
                detected["business_layer"].append(type_name)
                break
    
    # 数据层检测（基于 SQL）
    sql_upper = ground_truth_sql.upper()
    if "JOIN" in sql_upper or "INNER" in sql_upper or "LEFT" in sql_upper:
        detected["data_layer"].append("路径歧义")
    
    if len(ground_truth_sql) > 200:
        detected["data_layer"].append("复杂映射")
    
    # 跨层耦合检测
    if len(detected["user_layer"]) > 0 and len(detected["business_layer"]) > 0:
        detected["cross_layer"] = True
    if len(detected["business_layer"]) > 0 and len(detected["data_layer"]) > 0:
        detected["cross_layer"] = True
    if len(detected["user_layer"]) > 0 and len(detected["data_layer"]) > 0:
        detected["cross_layer"] = True
    
    return detected

def main():
    # 加载测试数据
    with open(os.path.expanduser(TEST_DATA)) as f:
        test_cases = json.load(f)
    
    print(f"分析 {len(test_cases)} 条测试数据...")
    
    results = []
    stats = {
        "total": len(test_cases),
        "has_ambiguity": 0,
        "user_layer": 0,
        "business_layer": 0,
        "data_layer": 0,
        "cross_layer": 0
    }
    
    # 分析每条查询
    for tc in test_cases:
        ambiguity = detect_ambiguity(tc["question"], tc["ground_truth_sql"])
        
        has_amb = (len(ambiguity["user_layer"]) > 0 or 
                   len(ambiguity["business_layer"]) > 0 or 
                   len(ambiguity["data_layer"]) > 0)
        
        if has_amb:
            stats["has_ambiguity"] += 1
        if len(ambiguity["user_layer"]) > 0:
            stats["user_layer"] += 1
        if len(ambiguity["business_layer"]) > 0:
            stats["business_layer"] += 1
        if len(ambiguity["data_layer"]) > 0:
            stats["data_layer"] += 1
        if ambiguity["cross_layer"]:
            stats["cross_layer"] += 1
        
        results.append({
            "id": tc["id"],
            "difficulty": tc["difficulty"],
            "question": tc["question"],
            "ambiguity": ambiguity,
            "has_ambiguity": has_amb
        })
    
    # 打印统计
    print("\n=== 歧义统计 ===")
    print(f"总查询数: {stats['total']}")
    print(f"有歧义查询: {stats['has_ambiguity']} ({stats['has_ambiguity']/stats['total']*100:.1f}%)")
    print(f"\n分层统计:")
    print(f"  用户层歧义: {stats['user_layer']} ({stats['user_layer']/stats['total']*100:.1f}%)")
    print(f"  业务层歧义: {stats['business_layer']} ({stats['business_layer']/stats['total']*100:.1f}%)")
    print(f"  数据层歧义: {stats['data_layer']} ({stats['data_layer']/stats['total']*100:.1f}%)")
    print(f"\n跨层耦合: {stats['cross_layer']} ({stats['cross_layer']/stats['total']*100:.1f}%)")
    
    # 打印典型跨层耦合案例
    cross_layer_cases = [r for r in results if r["ambiguity"]["cross_layer"]]
    print(f"\n=== 跨层耦合典型案例 (前5条) ===")
    for r in cross_layer_cases[:5]:
        print(f"\n[ID: {r['id']}] [{r['difficulty']}]")
        print(f"Q: {r['question'][:150]}...")
        print(f"歧义类型:")
        print(f"  用户层: {r['ambiguity']['user_layer']}")
        print(f"  业务层: {r['ambiguity']['business_layer']}")
        print(f"  数据层: {r['ambiguity']['data_layer']}")
    
    # 保存结果
    output_path = os.path.expanduser(f"{OUTPUT_DIR}/ambiguity_analysis.json")
    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": "2026-04-15",
            "stats": stats,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    main()