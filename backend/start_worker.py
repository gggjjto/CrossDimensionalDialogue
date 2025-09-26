#!/usr/bin/env python3
"""
启动AI任务处理Worker
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.workers.worker_script import start_worker

if __name__ == "__main__":
    # 从命令行参数获取队列名称
    queue_names = sys.argv[1:] if len(sys.argv) > 1 else None
    start_worker(queue_names)
