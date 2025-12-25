"""
MySQL Session Prometheus Exporter 启动脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main()