# -*- coding: utf-8 -*-
# @Time    : 2020/5/12 16:38
# @Author  : LY
import os
from mouse_keyboard_tool import *
from capture_findPicture_tool import find_picture,window_capture
import cv2 as cv
import numpy as np

# 读取图像
def cv_imread(file_path):
    cv_img = cv.imdecode(np.fromfile(file_path, dtype=np.uint8), cv.IMREAD_COLOR)
    return cv_img

def clect_course(course1):
    """
    :param course1: 选择录屏的课程的大类  todo:能同时选择多个大类
    :param course2: 该课程的大类下的子类
    :return: 返回所选课程的相对目录
    """
    time.sleep(4)  # 等待所有课程加载完毕
    course1_url = ''
    if course1 == '学习视频':
        mouse_left_click(60, 187, 2)
        course1_url = r'capture/Learning_video/'
    elif course1 == '就业课程':
        mouse_left_click(164, 190, 2)
        course1_url = r'capture/就业课程/'
    elif course1 == '拓展课程':
        mouse_left_click(269, 190, 2)
        course1_url = r'capture/outward_bound_course/'
    elif course1 == '基础班课程':
        mouse_left_click(374, 188, 2)
        course1_url = r'capture/Basic_course/'
    else:
        print('找不到该课程!!!')
    return course1_url


def confirm_course(course1, list_course2):
    '''
    :param list_course2: 传入2级课程名称列表，若有all字段，表示录屏本软件已有的全部课程
    :return: 返回准备录屏的2级课程目录

    '''
    course1_url= clect_course(course1)
    # 返回本程序已存储的所有该1级课程下的2级课程列表
    picture_list = os.listdir(course1_url)
    # print(f'picture_list:{picture_list}')
    select_course2 = []
    for course2 in list_course2:  # 遍历自选的2级课程
        if (course2 == 'all') | (course2 == 'All') | (course2 == 'ALL'):
            # 有all字段则把已有所有课程全加入录屏列表中
            for picture in picture_list:
                course2_path = course1_url + picture
                select_course2.append(course2_path)
        else:
            course2_path = course1_url + course2+'.png'
            if os.path.exists(course2_path):
                select_course2.append(course2_path)
            else:
                print(f'获取: {course1} -> {os.path.basename(course2_path)[:-4] } 失败！(◔‸◔?)')
    return select_course2


def find_whell_move(heigh, course2=None):
    '''找到并移动滚动条到高为height的位置，
    若course2为空，随便点击一个课程位置，
    若course2不为空，返回该课程的位置point
    '''
    view_handle = auto_FindWindow('Qt5QWindowIcon', 'TLIAS客户端')
    point1 = find_picture('capture/滚动条.png', view_handle)
    mouse_left_click_move(point1[0], point1[1], point1[0], heigh)
    time.sleep(2)
    if not course2:
        mouse_left_click(400, heigh)
        point = None
    else:
        point = find_picture(course2, view_handle)
    time.sleep(1)
    return point


def click_into_course2(course2_path):
    """# 点击course2的课程坐标，若没下载先点总下载,然后点击进入课程"""
    # course2_path 示例：'capture/outward_bound_course/python运维开发.png'
    view_handle = auto_FindWindow('Qt5QWindowIcon', 'TLIAS客户端')
    # 返回该窗口左上角和右下角坐标
    left_x, left_y, right_x, right_y = win32gui.GetWindowRect(view_handle)
    num = 'down_roll'
    wheel = 0
    while True:
        course2_name = os.path.basename(course2_path)[:-4]
        point= find_picture(course2_path, view_handle)
        # print(f'point:{point}')
        # 找到目标课程后，如果该课程没有下载完毕，点击下载
        if len(point) :
            flag = False
            while True:
                # 找到所有下载按钮列表
                download_list = find_picture(r'capture\4级课程下载课程按钮.png',view_handle)
                if download_list:
                    # print(f'download_list:{download_list}')
                    for download in download_list:
                        abs_h = abs(download[1]-point[0][1])
                        if abs_h<25:
                            x1 = download[0] - 20
                            y1 = download[1] - 20
                            w = 40
                            h = 40
                            mouse_left_click(download[0], download[1], 1)
                            mouse_move(0, 0)
                            flag = True
                            time.sleep(1)
                            break
                if flag:
                    img = window_capture(None,(x1,y1,w,h))
                    # print(f'img:{x1,y1,w,h}')
                    result = find_picture('capture\课程全部下载成功符号.png',target_img=img,num_storey=1)
                    if result:
                        # cv.imshow('img', img)
                        # cv.waitKey(-1)
                        # cv.destroyAllWindows()
                        print(f'{course2_name} 课程已下载完毕,即将进入该课程录制')
                        break
                    else:
                        time.sleep(10)
                        print(f'{course2_name} 课程下载中，请稍等')
                if not flag:
                    break

            # 获得进入该2级课程按钮的坐标
            into_course2 = (965,point[0][1])
            mouse_left_click(into_course2[0],into_course2[1],2)
            print(f'进入【{course2_name}】课程')
            return True
        else:
            # 向下滚动
            if num=='down_roll':
                # 鼠标滚轮向下滚动500像素
                mouse_wheel(300, 555, -500)
                wheel += 1
                if wheel > 3:
                    num = 'up_roll'
                    wheel = 0
                time.sleep(0.5)

            # 向上滚动
            elif num == 'up_roll':
                # 鼠标滚轮向上滚动500像素
                mouse_wheel(300,555,500)
                wheel += 1
                if wheel > 3:
                    num = 'fail'
                    wheel = 0
                time.sleep(0.5)
            # 查找失败
            elif num=='fail':
                print(f'查找【{course2_name}】进入课程按钮失败👈👈👈👈👈👈👈👈👈👈')
                print(f'将跳过此课程，直接下载下一课程！！')
                return False

if __name__ == '__main__':
    click_into_course2(r'capture\outward_bound_course\AI医生项目.png')