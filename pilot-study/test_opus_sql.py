#!/usr/bin/env python3
"""
Pilot Study Phase 1C: 使用 Opus API 进行 SQL 生成测试
"""

import json
import os
import requests
import time
from datetime import datetime

TEST_DATA = "~/agent-work/research/DA-disambiguation/pilot-study/test_cases_100.json"
OUTPUT_DIR = "~/agent-work/research/DA-disambiguation/pilot-study"

# Opus API 配置（来自 TOOLS.md）
API_BASE = "https://au.b4a.dev/v1/messages"
API_KEY = "sk-9d01bb5cad7a25fb-dezrb6-42dc6184"
MODEL = "cc/claude-opus-4-6"

def call_opus_sql(question, evidence, db_schema_hint=""):
    """调用 Opus API 生成 SQL"""
    
    system_prompt = """You are an expert SQL query generator. 
Given a natural language question and optional evidence/hints, generate the correct SQL query.
Output ONLY the SQL query, no explanations or markdown formatting."""

    user_prompt = f"""Question: {question}
Evidence: {evidence}

Generate the SQL query (output only the SQL, no explanation):"""

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "max_tokens": 500,
        "stream": False,
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        response = requests.post(
            API_BASE,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        if "content" in result:
            for block in result["content"]:
                if block["type"] == "text":
                    sql = block["text"].strip()
                    # 清理可能的 markdown 格式
                    if sql.startswith("```"):
                        sql = sql.split("```")[1].strip()
                        if sql.startswith("sql"):
                            sql = sql[3:].strip()
                    return sql, None
        return None, "No content in response"
    except Exception as e:
        return None, str(e)

def compare_sql(generated, ground_truth):
    """简单 SQL 对比"""
    # 标准化
    gen_norm = generated.lower().replace("\n", " ").strip()
    gt_norm = ground_truth.lower().replace("\n", " ").strip()
    
    # 完全匹配
    if gen_norm == gt_norm:
        return "exact_match"
    
    # 关键词匹配
    gt_keywords = set(gt_norm.split())
    gen_keywords = set(gen_norm.split())
    overlap = len(gt_keywords & gen_keywords) / len(gt_keywords) if gt_keywords else 0
    
    if overlap > 0.8:
        return "high_similarity"
    elif overlap > 0.5:
        return "partial_match"
    else:
        return "mismatch"

def main():
    # 加载测试数据
    with open(os.path.expanduser(TEST_DATA)) as f:
        test_cases = json.load(f)
    
    print(f"测试数据条数: {len(test_cases)}")
    print(f"开始时间: {datetime.now()}")
    print("使用 Opus API 进行 SQL 生成测试...")
    
    # 先测试 20 条
    test_subset = test_cases[:20]
    
    results = []
    stats = {
        "total": 0,
        "exact_match": 0,
        "high_similarity": 0,
        "partial_match": 0,
        "mismatch": 0,
        "errors": 0
    }
    
    for tc in test_subset:
        stats["total"] += 1
        print(f"\n[{tc['id']}] [{tc['difficulty']}] Testing...")
        print(f"  Q: {tc['question'][:80]}...")
        
        generated_sql, error = call_opus_sql(tc["question"], tc["evidence"])
        
        if error:
            print(f"  Error: {error[:100]}")
            stats["errors"] += 1
            results.append({
                "id": tc["id"],
                "status": "error",
                "error": error
            })
            continue
        
        match_result = compare_sql(generated_sql, tc["ground_truth_sql"])
        stats[match_result] += 1
        
        print(f"  Generated: {generated_sql[:100]}...")
        print(f"  Ground Truth: {tc['ground_truth_sql'][:100]}...")
        print(f"  Result: {match_result}")
        
        results.append({
            "id": tc["id"],
            "difficulty": tc["difficulty"],
            "question": tc["question"],
            "generated_sql": generated_sql,
            "ground_truth": tc["ground_truth_sql"],
            "match_result": match_result
        })
        
        # 避免 API 限流
        time.sleep(2)
    
    # 保存结果
    output_path = os.path.expanduser(f"{OUTPUT_DIR}/opus_sql_results.json")
    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "model": MODEL,
            "stats": stats,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== 统计结果 ===")
    print(f"总数: {stats['total']}")
    print(f"精确匹配: {stats['exact_match']}")
    print(f"高度相似: {stats['high_similarity']}")
    print(f"部分匹配: {stats['partial_match']}")
    print(f"不匹配: {stats['mismatch']}")
    print(f"错误: {stats['errors']}")
    
    accuracy = (stats['exact_match'] + stats['high_similarity']) / stats['total'] * 100
    print(f"\n准确率 (精确+高度相似): {accuracy:.1f}%")
    
    print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    main()