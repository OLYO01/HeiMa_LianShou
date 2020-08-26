# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 15:52
# @Author  : LY

import os
import ctypes, sys
import logging
import traceback
import json
from config import DIR_PATH, course2_download_list, SAVE_PATH, Record_PATH, BREAK_POINT_RECORD, course1_download
from start_exe_tool import run_exe,check_exe
from mouse_keyboard_tool import *
from capture_findPicture_tool import find_picture
from into_course2 import click_into_course2, confirm_course
from into_course3 import check_course2, title_location, path_if_exist, move_win


# 设置出错的日志
def log_init():
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: \n%(message)s")
    log_path = os.getcwd() + r'\Logs\log.txt'
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    """ch对象用于输出信息到日志文件"""
    fh = logging.FileHandler(log_path, mode='a', encoding='utf8')
    fh.setLevel(logging.WARNING)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def login():
    """
    打开并登录TLIAS客户端
    """
    login_handle = auto_FindWindow(None, 'TLIAS客户端-登录')
    left_x, left_y, right_x, right_y = win32gui.GetWindowRect(login_handle)
    w = int(right_x - left_x)
    h = int(right_y - left_y)
    login_point = find_picture(r'capture\黑马账号登录按钮.png', None, pos=(left_x, left_y, w, h))
    if login_point:
        x = login_point[0][0] + left_x
        y = login_point[0][1] + left_y
        mouse_left_click(x, y)
        print('已登录TLIAS客户端,即将进入登录后界面...')
    elif not login_point:
        raise Exception('没找到账号登录按钮，程序终止！')


def breakpoint_record():
    """
    用于断点录屏
    :return:
    """
    import json
    break_point_record = False
    num = 0
    list_imgs = [r'capture\memory_archive\course4.png', r'capture\memory_archive\course3.png',
                 r'capture\memory_archive\course2.png',
                 r'capture\memory_archive\break_point_recording']
    for file in list_imgs:
        if path_if_exist(file):
            num += 1

    if not BREAK_POINT_RECORD:
        # 如果断点续录配置文件为False,主动询问是否断点续录
        while str(num) == '4':
            word = input('发现曾经录屏未完整，是否继续录屏？\n输入‘Y’表示继续断点续录\n输入‘N’表示删除断点记忆\n')
            if (word == 'Y') or (word == 'y'):
                break_point_record = True
                break
            if (word == 'N') or (word == 'n'):
                # 删除断点续录记忆
                list_imgs = [r'capture\memory_archive\course4.png', r'capture\memory_archive\course3.png',
                             r'capture\memory_archive\course2.png',
                             r'capture\memory_archive\break_point_recording']
                for file in list_imgs:
                    if path_if_exist(file):
                        os.remove(file)
                print("已删除断点续录记忆")
                break
    # 如果配置文件中：BREAK_POINT_RECORD=True且断点续录文件齐全
    elif BREAK_POINT_RECORD and (str(num) == '4'):
        break_point_record = True
    if break_point_record:
        with open(r'capture\memory_archive\break_point_recording', 'r', encoding='utf8') as f:
            json_info = f.read()
        dict_info = json.loads(json_info)
        course1 = dict_info['course1']
        course2_path = dict_info['course2_path']
        save_path_course2 = dict_info['save_path_course2']
        course1_dict = {'双元视频': (53, 189),
                        '就业课程': (165, 189),
                        '拓展课程': (267, 189),
                        '基础班课程': (375, 189),
                        '授课视频': (485, 189)
                        }
        course1_point = course1_dict[course1]
        mouse_left_click(course1_point[0], course1_point[1], 2)
        click_into_course2(course2_path)
        check_course2(course1, course2_path)
        title_location(course1, course2_path, save_path_course2, True)


def open_course(course1, select_course2_list, save_path=None):
    """
    :return:
    :param course1: 1级课程名 示例：'拓展课程'
    :param select_course2_list: 二级课程自选列表 示例：['shell与运维22','python运维开发','AI医生项目']
    :param save_path: 录屏存放的绝对目录  示例："G:\\下载\\黑马视频"
    :return:
    """
    try:
        path_if_exist(save_path, True)
    except Exception:
        print(f'创建目录 {save_path} 失败，程序终止！\n'
              f'请手动创建该目录后再重新启动程序')
        exit()
    # 获得该1级课程的保存路径
    save_path_course1 = save_path + '\\' + course1
    # 返回待录屏的2级课程的图片路径组成的列表
    select_course2 = confirm_course(course1, select_course2_list)
    course2_list = {'course2': select_course2}
    json_info = json.dumps(course2_list)
    with open(r'capture\memory_archive\course2_list', 'w', encoding='utf8') as f:
        f.write(json_info)
    # 每次取出自选2级课程的图片路径
    while True:
        with open(r'capture\memory_archive\course2_list', 'r', encoding='utf8') as f:
            json_info = f.read()
        course2_list_info = json.loads(json_info)
        course2_list = course2_list_info['course2']
        # 从2级列表中pop出一个课程
        try:
            course2_path = course2_list.pop(0)
        except:
            print("所有课程全部下载结束！")
            list_imgs = [r'capture\memory_archive\course4.png', r'capture\memory_archive\course3.png',
                         r'capture\memory_archive\course2.png',
                         r'capture\memory_archive\break_point_recording']
            for file in list_imgs:
                if path_if_exist(file):
                    os.remove(file)
            print("已删除断点续录记忆")
            exit()
        # 保存剩下的course2课程列表
        course2_list = {'course2': course2_list}
        json_info = json.dumps(course2_list)
        with open(r'capture\memory_archive\course2_list', 'w', encoding='utf8') as f:
            f.write(json_info)
        time.sleep(2)
        course2_name = os.path.basename(course2_path)[:-4]
        save_path_course2 = save_path_course1 + '\\' + course2_name
        download_over = path_if_exist(str(save_path_course2) + '\\' + 'course2.png')
        if download_over:
            print(f'已跳过下载完毕课程：{course2_name}')
            continue
        result = click_into_course2(course2_path)
        if not result:
            continue
        check_course2(course1, course2_path)
        title_location(course1, course2_path, save_path_course2)


def start_record_exe(PATH):
    # 启动录屏软件客户端
    run_exe(PATH)
    hwnd = auto_FindWindow('Hi! oCam')
    left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)
    w = int(right_x - left_x)
    h = int(right_y - left_y)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 1300, 750, w, h, win32con.SWP_SHOWWINDOW)
    win32gui.SetForegroundWindow(hwnd)
    result = find_picture(r'capture\录屏软件最小化按钮.png', hwnd, times=3)
    if result:
        mouse_left_click(result[0][0], result[0][1])
    num = 0
    while True:
        num += 20
        mouse_move(num, 1060)
        time.sleep(0.01)
        if num >= 1920:
            break


def start_TLIAS_exe(PATH):
    # 启动TLIAS客户端
    run_exe(PATH)
    login()
    move_win()
    time.sleep(1)

def main():
    """
    程序入口
    """
    if is_admin():
        restart = True
        log = log_init()
        while restart:
            # 如果报错，重启程序，继续录制
            try:
                # 关闭循环
                restart = False
                hightlight_old_window()
                start_TLIAS_exe(DIR_PATH)
                start_record_exe(Record_PATH)
                二级课程自选列表 = course2_download_list  # '百度人工智能课程'
                save_path = SAVE_PATH
                breakpoint_record()
                open_course(course1_download, 二级课程自选列表, save_path)
            except Exception:
                error_data = traceback.format_exc()
                log.error(error_data)
                restart = True
                print('出现一次意外报错！⊙﹏⊙‖∣，已重新启动程序', '*' * 50)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def test():
    # 命令行窗口标题C:\Windows\system32\cmd.exe
    if is_admin():
        # 调整命令窗口布局
        hightlight_old_window()
        # # 启动TLIAS客户端
        # start_TLIAS_exe(DIR_PATH)
        # # 启动录屏软件客户端
        # start_record_exe(Record_PATH)
    else:
        # 弹出UAC提权窗口，提权成功后会新开管理员权限窗口运行后续代码
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

def hightlight_old_window():
    """
    遍历windows 所有可显示的窗口句柄及窗口标题，以确定该程序是否多开，关闭多开的程序
    """
    # 检测是否入口程序是否在运行
    # bat和pycharm普通启动会开新窗口
    interpreter_path = r'\env_LY\Scripts\python.exe'
    abs_path = os.path.abspath(__file__)
    window_path = os.path.dirname(abs_path) + interpreter_path
    # 把window_path转换成符合当前系统的分隔符，2个替换有一个会生效
    Window_abs_path = window_path.replace('/', os.sep)
    Window_abs_path = Window_abs_path.replace('\\', os.sep)
    # 输出结果应该为：E:\Desktop\test1\env_LY\Scripts\python.exe
    # print(f'Window_abs_path: {Window_abs_path}')
    LPARAM = None
    hwnds = []
    def get_all_hwnd(hwnd,LPARAM2):
        """
        :param hwnd: 接收win32gui.EnumWindows遍历传来的窗口句柄
        :param LPARAM2: 接收win32gui.EnumWindows传来的自定义参数
        """
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            # 如果该窗口句柄标题和入口程序相同
            if win32gui.GetWindowText(hwnd)==Window_abs_path:
                # 加入匹配到的窗口句柄到窗口句柄列表中
                hwnds.append(hwnd)
            # 窗口被点选后，标题会多出选择二字
            if win32gui.GetWindowText(hwnd) == ('选择'+Window_abs_path):
                # 加入匹配到的窗口句柄到窗口句柄列表中
                hwnds.append(hwnd)
    # print(f'hwnds: {hwnds}')
    # 遍历所有窗口的句柄依次传递给回调函数，同时再给回调函数传参
    win32gui.EnumWindows(get_all_hwnd,LPARAM)
    # 还原窗口，后开启的窗口句柄会在hwnds靠后的索引位置
    win32gui.SendMessage(hwnds[0], win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
    # 移动窗口位置
    win32gui.SetWindowPos(hwnds[0], win32con.HWND_TOPMOST, 1110, 0, 805, 1030, win32con.SWP_SHOWWINDOW)
    # 使该句柄窗口为当前活动窗口：最顶层显示
    win32gui.SetForegroundWindow(hwnds[0])
    if len(hwnds)>=2:
        # 退出本程序，留下旧窗口
        exit()


if __name__ == '__main__':
    main()
    # test()
    # C:\Users\LY\AppData\Local\Temp\oCam\oCam