#!/usr/bin/env python3
"""
Pilot Study: 使用 qwen3.5-plus 进行 SQL 生成测试
通过 sessions_spawn 调用模型
"""

import json
import os
import subprocess

TEST_DATA = "~/agent-work/research/DA-disambiguation/pilot-study/test_cases_100.json"
OUTPUT_DIR = "~/agent-work/research/DA-disambiguation/pilot-study"

def call_qwen_sql(question, evidence):
    """通过 OpenClaw sessions_spawn 调用 qwen3.5-plus"""
    
    prompt = f"""你是一个SQL专家。根据以下问题和提示，生成正确的SQL查询。
只输出SQL语句，不要解释。

问题: {question}
提示: {evidence}

SQL:"""
    
    # 使用 sessions_spawn 调用模型
    # 这里用简化的方式：直接调用模型API
    return prompt

def main():
    # 加载测试数据
    with open(os.path.expanduser(TEST_DATA)) as f:
        test_cases = json.load(f)
    
    print(f"测试数据条数: {len(test_cases)}")
    
    # 选择10条做测试
    test_subset = test_cases[:10]
    
    results = []
    
    for tc in test_subset:
        print(f"\n[ID: {tc['id']}] 测试中...")
        print(f"问题: {tc['question'][:100]}...")
        
        # 构建prompt
        prompt = call_qwen_sql(tc['question'], tc['evidence'])
        
        results.append({
            "id": tc['id'],
            "question": tc['question'],
            "ground_truth": tc['ground_truth_sql'],
            "prompt": prompt
        })
    
    # 保存结果供后续测试
    output_path = os.path.expanduser(f"{OUTPUT_DIR}/sql_test_prompts.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n已保存 {len(results)} 条测试prompt到: {output_path}")
    print("\n下一步: 使用模型API或sessions_spawn执行SQL生成")

if __name__ == "__main__":
    main()