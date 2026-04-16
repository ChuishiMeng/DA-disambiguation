#!/usr/bin/env python3
"""
Pilot Study Phase 1: 准备测试数据
从 BIRD-mini-dev 抽取 challenging 和 moderate 复杂查询
"""

import json
import os

# 数据路径
BIRD_DATA = "~/agent-work/datasets/BIRD-mini-dev/data/mini_dev_sqlite-00000-of-00001.json"
OUTPUT_DIR = "~/agent-work/research/DA-disambiguation/pilot-study"

def main():
    # 加载原始数据
    with open(os.path.expanduser(BIRD_DATA)) as f:
        data = json.load(f)
    
    print(f"原始数据条数: {len(data)}")
    
    # 筛选 challenging 和 moderate
    challenging = [d for d in data if d['difficulty'] == 'challenging']
    moderate = [d for d in data if d['difficulty'] == 'moderate']
    
    print(f"Challenging: {len(challenging)}")
    print(f"Moderate: {len(moderate)}")
    
    # 抽取前 50 challenging + 50 moderate (共100条)
    test_data = challenging[:50] + moderate[:50]
    
    # 简化格式，只保留必要字段
    test_cases = []
    for d in test_data:
        test_cases.append({
            "id": d["question_id"],
            "db_id": d["db_id"],
            "question": d["question"],
            "evidence": d["evidence"],
            "ground_truth_sql": d["SQL"],
            "difficulty": d["difficulty"]
        })
    
    # 保存测试数据
    output_path = os.path.expanduser(f"{OUTPUT_DIR}/test_cases_100.json")
    with open(output_path, 'w') as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    
    print(f"\n已保存 {len(test_cases)} 条测试数据到: {output_path}")
    
    # 打印前 3 条样例
    print("\n测试样例 (前3条):")
    for tc in test_cases[:3]:
        print(f"\n[ID: {tc['id']}] [{tc['difficulty']}]")
        print(f"Q: {tc['question'][:150]}...")
        print(f"Ground Truth: {tc['ground_truth_sql'][:150]}...")

if __name__ == "__main__":
    main()