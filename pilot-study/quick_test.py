#!/usr/bin/env python3
"""
快速 SQL 测试：测试 5 条典型案例
"""

import json
import os
import requests
from datetime import datetime

TEST_DATA = "~/agent-work/research/DA-disambiguation/pilot-study/test_cases_100.json"
OUTPUT_DIR = "~/agent-work/research/DA-disambiguation/pilot-study"

# Opus API
API_BASE = "https://au.b4a.dev/v1/messages"
API_KEY = "sk-9d01bb5cad7a25fb-dezrb6-42dc6184"
MODEL = "cc/claude-opus-4-6"

def call_opus(question, evidence):
    """单次调用"""
    prompt = f"""Generate SQL for this question. Output ONLY the SQL.

Question: {question}
Evidence: {evidence}

SQL:"""
    
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "max_tokens": 300,
        "stream": False,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        r = requests.post(API_BASE, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        for block in data.get("content", []):
            if block["type"] == "text":
                sql = block["text"].strip()
                if "```" in sql:
                    sql = sql.split("```")[1].replace("sql", "").strip()
                return sql
    except Exception as e:
        return f"ERROR: {e}"
    
    return "ERROR: no response"

def main():
    with open(os.path.expanduser(TEST_DATA)) as f:
        cases = json.load(f)
    
    # 选择 5 条 challenging 案例
    test = [c for c in cases if c['difficulty'] == 'challenging'][:5]
    
    print(f"测试 {len(test)} 条 challenging 案例...")
    
    for c in test:
        print(f"\n[ID:{c['id']}] {c['question'][:60]}...")
        sql = call_opus(c['question'], c['evidence'])
        print(f"Generated: {sql[:100]}...")
        print(f"Ground: {c['ground_truth_sql'][:100]}...")
        
        # 保存单条结果
        result = {
            "id": c['id'],
            "question": c['question'],
            "generated": sql,
            "ground_truth": c['ground_truth_sql']
        }
        
        with open(os.path.expanduser(f"{OUTPUT_DIR}/opus_quick_test.json"), 'a') as f:
            f.write(json.dumps(result) + "\n")

if __name__ == "__main__":
    main()