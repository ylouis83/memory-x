#!/usr/bin/env python3
from __future__ import annotations

"""
Mem0 端到端示例

步骤：
1) 安装 mem0:  pip install "git+https://github.com/mem0ai/mem0.git"
2) 运行本示例:  python examples/mem0_end_to_end.py

示例会：
- 使用 Mem0 作为长期记忆后端
- 写入两轮含有时间短语的对话（最近1周/近期 头痛）
- 检索与“头痛”相关的记忆
"""

import os
import sys
from typing import Dict


def main() -> int:
    try:
        # 延迟导入，便于给出明确提示
        from src.storage.mem0_store import Mem0MemoryStore  # type: ignore
    except Exception as e:
        print("[!] 未安装 mem0，无法运行 Mem0 示例。\n"
              "    请先执行:\n"
              "      pip install \"git+https://github.com/mem0ai/mem0.git\"\n"
              f"    详细错误: {e}")
        return 1

    from src.core.memory_manager import SimpleMemoryManager

    # 直接注入 Mem0 后端（不依赖环境变量）
    store = Mem0MemoryStore()
    mm = SimpleMemoryManager(user_id="demo_user", store=store)

    def add_turn(text: str, entities: Dict = None, importance: int = 3):
        ok = mm.add_conversation(
            user_message=text,
            ai_response="（示例）请注意休息，必要时就医。",
            entities=entities or {},
            intent="NORMAL_CONSULTATION",
            importance=importance,
        )
        print(f"写入: {text} -> {'OK' if ok else 'FAIL'}")

    # 两轮含时间短语的对话（触发时间归一化与合并逻辑；importance>=3 才会写入长期）
    add_turn("最近1周头痛，晚上更明显。", entities={'SYMPTOM': [('头痛', 0, 2)]})
    add_turn("近期还是头痛，白天稍好一些。", entities={'SYMPTOM': [('头痛', 0, 2)]})

    # 检索
    results = mm.retrieve_memories("头痛", top_k=5)
    print("\n检索结果（top-5）:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. score={r.get('score', 0):.3f} | {r.get('content','')[:60]}")

    # 打印统计
    stats = mm.get_memory_stats()
    print("\n统计:")
    for k, v in stats.items():
        print(f"  - {k}: {v}")

    print("\n完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

