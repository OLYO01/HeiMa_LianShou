# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 16:44
# @Author  : LY
import win32ui
import cv2 as cv
from PIL import Image
import numpy as np
import math
from mouse_keyboard_tool import *


def window_capture(hwnd=None, pos=None):
    '''
    截图功能
    '''
    if hwnd == None:
        hwnd = 0
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    if pos == None:
        left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)
        x1 = 0
        y1 = 0
        w = right_x - left_x  # 截图的宽
        h = right_y - left_y  # 截图的高
    else:
        x1 = pos[0]
        y1 = pos[1]
        w = pos[2]
        h = pos[3]
    # 创建位图对象准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    # 保存bitmap到内存设备描述表
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (x1, y1), win32con.SRCCOPY)
    # 从内存中读取位图信息
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    im_PIL = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    BGR_img = cv.cvtColor(np.asarray(im_PIL), cv.COLOR_RGB2BGR)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    # 返回BGR图像
    return BGR_img


# 读取图像
def cv_imread(file_path):
    cv_img = cv.imdecode(np.fromfile(file_path, dtype=np.uint8), cv.IMREAD_COLOR)
    return cv_img


def pyramid_demo(image, num_storey):
    # 设置图像金字塔
    level = num_storey
    temp = image.copy()
    pyramid_images = []
    pyramid_images.append(temp)
    for i in range(level - 1):
        dst = cv.pyrDown(temp)
        pyramid_images.append(dst)
        temp = dst.copy()
    return pyramid_images


def filter_pt(pts, num=7):
    '''
    过滤位置相近的点的坐标
    :param pts: 相似的元祖组成的列表
    :param num: 过滤的最大相似值
    :return: 返回过滤后的元祖列表
    '''
    filter_pts = []
    while pts:
        cur_pt = pts.pop(0)
        filter_pts.append(cur_pt)
        # 临时存放相似点的列表
        aa = []
        for i in pts:
            if (abs(cur_pt[0] - i[0]) + abs(cur_pt[1] - i[1])) < num:
                aa.append(i)
        for a in aa:
            pts.remove(a)
    return filter_pts


def find_picture_basic(template, hwnd=None, pos=None, target_img=None, num_storey=4, t=0.8, show_img=False,
                 tpl_is_memory=False, one_point=True):
    """
    目标匹配功能
    """
    target = None
    left_x = 0  # todo 这可能会出错
    left_y = 0
    try:
        if tpl_is_memory:
            tpl = template
        else:
            tpl = cv_imread(template)
    except Exception as tpl_error:
        assert 0, f'载入模板图像失败！\n' \
                  f'报错信息：{str(tpl_error)}\n' \
                  f'已停止程序'

    try:
        if (hwnd == None) and (pos == None):
            target = target_img

        elif (hwnd == None) and (pos != None):
            target = window_capture(hwnd, pos)

        elif (hwnd != None) and (pos == None):
            target = window_capture(hwnd, pos)
            left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)

        elif (hwnd != None) and (pos != None):
            target = window_capture(hwnd, pos)
            left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)
        else:
            assert 0
    except Exception as target_error:
        assert 0, f'载入目标图像失败！\n' \
                  f'报错信息：{str(target_error)}\n' \
                  f'已停止程序'

    # 返回2个图像的高斯金字塔
    tpl_p = pyramid_demo(tpl, num_storey)
    target_p = pyramid_demo(target, num_storey)
    num = len(target_p)
    flag = False
    center_pts = []  # 存放找到图像的中心点
    for i in range(num):
        temp = target_p[i]
        for j in range(num):
            tp = tpl_p[j]
            result = cv.matchTemplate(temp, tp, cv.TM_CCOEFF_NORMED)
            pts = []
            if one_point:
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                if max_val < t:
                    return []
                if max_val >= t:
                    pts.append(max_loc)
            if not one_point:
                loc = np.where(result >= t)
                if loc[0].size == 0:
                    return []

                for pt in zip(*loc[::-1]):
                    pts.append(pt)
                pts = filter_pt(pts)
            # 遍历匹配到的图像左上点的列表
            for pt in pts:
                val = math.pow(2, i)
                pt_w = int(pt[0] * val)
                pt_h = int(pt[1] * val)
                tpl_h, tpl_w = tp.shape[:2]
                tpl_h = int(tpl_h * val)
                tpl_w = int(tpl_w * val)
                if show_img:
                    cv.rectangle(target, (pt_w, pt_h), (pt_w + tpl_w, pt_h + tpl_h), (0, 0, 255), 2, 8, 0)
                    target_h, target_w = target.shape[:2]
                    new_img = cv.resize(target, (target_w // 2, target_h // 2))
                    cv.imshow('new_img', new_img)
                    cv.moveWindow('new_img', 1200, 0)
                    cv.waitKey(-1)
                    cv.destroyAllWindows()
                try:
                    center_point = (pt_w + tpl_w // 2 + left_x, pt_h + tpl_h // 2 + left_y)
                    center_pts.append(center_point)
                    flag = True
                except:
                    print('匹配图像：求出相似图像的矩形中间点时，报错！\n'
                          '已退出程序！！！')
                    exit()
            if flag:
                break
        if flag:
            break
    # 返回找到图片的中心点在显示屏中的坐标的列表
    return center_pts

def find_picture(template, hwnd=None, pos=None, target_img=None, num_storey=4, t=0.8, show_img=False,
                 tpl_is_memory=False, one_point=True, times=1):
    while times:
        result = find_picture_basic(template=template, hwnd=hwnd, pos=pos,
                                    target_img=target_img, num_storey=num_storey,t=t, show_img=show_img,
                                    tpl_is_memory=tpl_is_memory,one_point=one_point)
        if result:
            return result
        times-=1
        if times==0:
            return []
        time.sleep(1)



def twice_find_picture(template1, template2, direction=1, num=8, hwnd=None, pos=None, target_img=None, num_storey=4,
                       t=0.8, show_img=False, tpl_is_memory=False, times=1):
    """
    二次查找图像
    """
    temp1_point_list = find_picture(template1, hwnd, pos, target_img, num_storey, t, False, tpl_is_memory,
                                    one_point=False, times=times)
    temp2_point_list = find_picture(template2, hwnd, pos, target_img, num_storey, t, False, tpl_is_memory,
                                    one_point=False, times=times)
    target_point_list = []
    for point1 in temp1_point_list:
        for point2 in temp2_point_list:
            p = abs(point1[direction] - point2[direction])
            if p <= num:
                target_point_list.append(point2)
    if show_img and tpl_is_memory:
        print('暂时没空做内存图像显图，有空再做！⊙﹏⊙‖∣')
    elif show_img and (tpl_is_memory == False):
        try:
            # 如果hwnd和pos都为None,则target_img接收内存图像
            if (hwnd == None) and (pos == None):
                target = target_img
                left_x = 0
                left_y = 0
            elif (hwnd == None) and (pos != None):
                target = window_capture(hwnd, pos)
                left_x = 0
                left_y = 0
            elif (hwnd != None) and (pos == None):
                target = window_capture(hwnd, pos)
                left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)
            elif (hwnd != None) and (pos != None):
                target = window_capture(hwnd, pos)
                left_x, left_y, right_x, right_y = win32gui.GetWindowRect(hwnd)
            else:
                # 不符合载入目标条件
                assert 0
        except Exception as target_error:
            assert 0, f'载入目标图像失败！\n' \
                      f'f报错信息：{str(target_error)}\n' \
                      f'已停止程序'
        tpl2_img = cv_imread(template2)
        h, w = tpl2_img.shape[:2]
        w = w // 2
        h = h // 2
        for pt in target_point_list:
            pt_x = pt[0] - left_x
            pt_y = pt[1] - left_y

            cv.rectangle(target, (pt_x - w, pt_y - h), (pt_x + w, pt_y + h), (0, 0, 255), 2, 8, 0)
        # target_h, target_w = target.shape[:2]
        # target = cv.resize(target, (target_w // 2, target_h // 2))
        cv.imshow('new_img', target)
        cv.moveWindow('new_img', 1200, 0)
        cv.waitKey(1000)
        cv.destroyAllWindows()

    return target_point_list


if __name__ == '__main__':
    from mouse_keyboard_tool import auto_FindWindow

    view_handle = auto_FindWindow('Qt5QWindowIcon', 'TLIAS客户端')
    img_1 = cv_imread(r'capture\outward_bound_course\nlp自然语言处理.png')
    img_2 = cv_imread(r'G:\下载\3.png')
    # result = find_picture(r'capture\outward_bound_course\nlp自然语言处理.png', hwnd=view_handle, show_img=True, times=20)
    result = twice_find_picture(img_1, img_2, 1, 8, view_handle, tpl_is_memory=True, show_img=True,times = 20)
    print(result)
