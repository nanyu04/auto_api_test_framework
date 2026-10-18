"""
【测试入口】— 统一运行脚本

用法：
    python run.py              # 运行全部用例
    python run.py -m smoke     # 冒烟测试
    python run.py -n 4         # 4 进程并行
    python run.py --report     # 运行 + 生成 Allure 报告
"""
import sys
import subprocess
from pathlib import Path


def run_tests():
    """
    执行 pytest，命令行参数原样透传。

    例：python run.py -m smoke --report  →  pytest -v -m smoke --alluredir reports/allure
    """
    args = sys.argv[1:]

    # 组装 pytest 命令
    cmd = ["pytest"]

    if "-v" not in args and "--quiet" not in args and "-q" not in args:
        cmd.append("-v")

    # 生成 Allure 报告
    if "--report" in args:
        args.remove("--report")
        cmd.extend(["--alluredir", "reports/allure"])
        cmd.extend(args)
        subprocess.run(cmd, cwd=Path(__file__).parent)
        subprocess.run(["allure", "serve", "reports/allure"], cwd=Path(__file__).parent)
    else:
        cmd.extend(args)
        subprocess.run(cmd, cwd=Path(__file__).parent)


if __name__ == "__main__":
    run_tests()
