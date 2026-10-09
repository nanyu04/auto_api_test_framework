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
    #这个args=sys.argv 是用于读取你输入的指令
    python run_tests.py -k test_login --report
    sys.argv = ['run_tests.py', '-k', 'test_login', '--report']
    这里的1就是代表后面的第几个开始
    args = sys.argv[1:] = ['-k', 'test_login', '--report']

    """
    args = sys.argv[1:]

    # 构建 pytest 命令  创建一个列表cmd pytest是第一个参数
    cmd = ["pytest"]

    # 默认 -v
    if "-v" not in args and "--quiet" not in args and "-q" not in args:
        cmd.append("-v")

    # 是否生成报告
    if "--report" in args:
        args.remove("--report")
        #extend将["--alluredir", "reports/allure"]拆开，一个一个加入cmd列表
        cmd.extend(["--alluredir", "reports/allure"])
        cmd.extend(args)
        #打开cmd 跑命令
        subprocess.run(cmd, cwd=Path(__file__).parent)
        # 打开报告
        subprocess.run(["allure", "serve", "reports/allure"], cwd=Path(__file__).parent)
    else:
        cmd.extend(args)
        # 进入 cwd 的目录 然后运行cmd 的命令
        subprocess.run(cmd, cwd=Path(__file__).parent)

if __name__ == "__main__":
    run_tests()