# -*- coding: utf-8 -*-
# @Time    : 2020/5/3 23:40
# @Author  : LY

import os
import psutil
from config import DIR_PATH,Record_PATH


def check_exe(DIR_PATH,kill_exe=True):
    """
    把指定路径程序名与进程中运行的程序名比对，若发现同名则强制停止该进程
    :param DIR_PATH:
    :return:
    """
    base_name = os.path.basename(DIR_PATH)
    running_pids = psutil.pids()
    for pid in running_pids:
        p = psutil.Process(pid)
        if p.name() == base_name:
            if kill_exe:
                print(f"关闭{base_name}程序")
                # command_str = f'2@> /dev/null taskkill /F /T /IM {base_name}'
                command_str = f'taskkill /F /T /IM {base_name}'
                os.system(command_str)
                return 1
            print(f"{base_name}程序正在运行中,请手动关闭该程序...")

def run_exe(DIR_PATH):
    """
    启动该exe程序
    :param DIR_PATH: 目标exe的绝对路径
    :return:y
    """
    check_exe(DIR_PATH)
    base_name = os.path.basename(DIR_PATH)
    print(f"运行{base_name}程序")
    os.system(f'start {DIR_PATH}')


if __name__ == '__main__':
    # run_exe(Record_PATH)
    # run_exe(DIR_PATH)
    check_exe(r'E:\Desktop\test1\env_LY\Scripts\python.exe')
