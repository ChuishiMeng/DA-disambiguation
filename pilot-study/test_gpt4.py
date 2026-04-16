#!/usr/bin/env python3
"""
Pilot Study: LLM SQL 生成测试脚本
使用可用模型（qwen3.5-plus / glm-5）进行SQL生成
"""

import json
import os
import time
import requests
from datetime import datetime

# 配置
TEST_DATA = "~/agent-work/research/DA-disambiguation/pilot-study/test_cases_100.json"
OUTPUT_DIR = "~/agent-work/research/DA-disambiguation/pilot-study"

# Bailian API 配置
API_BASE = os.environ.get("BAILIAN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
API_KEY = os.environ.get("BAILIAN_API_KEY", "")
MODEL = "qwen3.5-plus"  # 可选: glm-5, kimi-k2.5

def call_gpt4(question, evidence, db_schema_hint=""):
    """调用 GPT-4 生成 SQL"""
    
    system_prompt = """You are an expert SQL query generator. 
Given a natural language question and optional evidence/hints, generate the correct SQL query.
Output ONLY the SQL query, no explanations."""

    user_prompt = f"""Question: {question}
Evidence: {evidence}
{db_schema_hint}

Generate the SQL query:"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.0  # 确定性输出
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        sql = result["choices"][0]["message"]["content"].strip()
        return sql, None
    except Exception as e:
        return None, str(e)

def compare_sql(generated, ground_truth):
    """简单 SQL 对比（可改进为语义对比）"""
    # 标准化：去除空格、换行
    gen_norm = generated.lower().replace("\n", " ").strip()
    gt_norm = ground_truth.lower().replace("\n", " ").strip()
    
    # 完全匹配
    if gen_norm == gt_norm:
        return "exact_match"
    
    # 关键词匹配（简单检查）
    gt_keywords = set(gt_norm.split())
    gen_keywords = set(gen_norm.split())
    overlap = len(gt_keywords & gen_keywords) / len(gt_keywords)
    
    if overlap > 0.8:
        return "high_similarity"
    elif overlap > 0.5:
        return "partial_match"
    else:
        return "mismatch"

def analyze_failure(test_case, generated_sql):
    """分析失败案例的歧义类型"""
    question = test_case["question"]
    evidence = test_case["evidence"]
    ground_truth = test_case["ground_truth_sql"]
    
    # 基于关键词的歧义类型推断
    ambiguity_types = []
    
    # 用户层歧义信号
    user_signals = ["my", "our", "its", "their", "this", "that", "recent", "latest"]
    if any(s in question.lower() for s in user_signals):
        ambiguity_types.append("user_layer")
    
    # 业务层歧义信号
    biz_signals = ["ratio", "average", "percentage", "difference", "increase", "decrease", 
                   "best", "worst", "most", "least", "top", "bottom"]
    if any(s in question.lower() for s in biz_signals):
        ambiguity_types.append("business_layer")
    
    # 数据层歧义信号（多表、复杂 JOIN）
    if "JOIN" in ground_truth.upper() or "INNER" in ground_truth.upper():
        ambiguity_types.append("data_layer")
    
    if len(ground_truth) > 200:  # 复杂 SQL
        ambiguity_types.append("complex_query")
    
    if len(ambiguity_types) == 0:
        ambiguity_types.append("unknown")
    
    return ambiguity_types

def main():
    # 加载测试数据
    with open(os.path.expanduser(TEST_DATA)) as f:
        test_cases = json.load(f)
    
    print(f"测试数据条数: {len(test_cases)}")
    print(f"开始时间: {datetime.now()}")
    
    if not API_KEY:
        print("\n⚠️ 未配置 API_KEY，请设置环境变量 OPENAI_API_KEY")
        print("或者手动提供 API 配置")
        return
    
    results = []
    stats = {
        "total": 0,
        "exact_match": 0,
        "high_similarity": 0,
        "partial_match": 0,
        "mismatch": 0,
        "errors": 0
    }
    
    ambiguity_stats = {
        "user_layer": 0,
        "business_layer": 0,
        "data_layer": 0,
        "complex_query": 0,
        "unknown": 0
    }
    
    for tc in test_cases[:10]:  # 先测试10条验证脚本
        stats["total"] += 1
        
        print(f"\n[{tc['id']}] [{tc['difficulty']}] Testing...")
        
        generated_sql, error = call_gpt4(tc["question"], tc["evidence"])
        
        if error:
            print(f"  Error: {error}")
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
        
        # 分析失败案例
        if match_result in ["partial_match", "mismatch"]:
            ambiguity_types = analyze_failure(tc, generated_sql)
            for at in ambiguity_types:
                ambiguity_stats[at] += 1
            print(f"  Ambiguity Types: {ambiguity_types}")
        
        results.append({
            "id": tc["id"],
            "difficulty": tc["difficulty"],
            "question": tc["question"],
            "generated_sql": generated_sql,
            "ground_truth": tc["ground_truth_sql"],
            "match_result": match_result,
            "ambiguity_types": ambiguity_types if match_result in ["partial_match", "mismatch"] else []
        })
        
        # 避免 API 限流
        time.sleep(1)
    
    # 保存结果
    output_path = os.path.expanduser(f"{OUTPUT_DIR}/results_phase1.json")
    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "ambiguity_stats": ambiguity_stats,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== 统计结果 ===")
    print(f"总数: {stats['total']}")
    print(f"精确匹配: {stats['exact_match']}")
    print(f"高度相似: {stats['high_similarity']}")
    print(f"部分匹配: {stats['partial_match']}")
    print(f"不匹配: {stats['mismatch']}")
    print(f"错误: {stats['errors']}")
    
    print(f"\n=== 歧义类型分布 ===")
    for k, v in ambiguity_stats.items():
        print(f"{k}: {v}")
    
    print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    main()