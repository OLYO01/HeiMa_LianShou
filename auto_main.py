# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 15:52
# @Author  : LY

import os
import logging
import traceback
import json
from config import DIR_PATH, course2_download_list, SAVE_PATH, Record_PATH, BREAK_POINT_RECORD,course1_download
from start_exe_tool import run_exe
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
    restart = True
    log = log_init()
    while restart:
        # 如果报错，重启程序，继续录制
        try:
            # 关闭循环
            restart = False
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


def test():
    start_TLIAS_exe(DIR_PATH)
    start_record_exe(Record_PATH)
    二级课程自选列表 = course2_download_list  # '百度人工智能课程'
    save_path = SAVE_PATH
    breakpoint_record()
    open_course(course1_download, 二级课程自选列表, save_path)


if __name__ == '__main__':
    main()
    # test()
    ##
