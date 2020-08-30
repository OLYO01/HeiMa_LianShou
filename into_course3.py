# -*- coding: utf-8 -*-
# @Time    : 2020/6/21 2:06
# @Author  : LY
import os
from mouse_keyboard_tool import *
from capture_findPicture_tool import find_picture, window_capture
from into_course2 import click_into_course2, clect_course
import cv2 as cv
import numpy as np
from BaiduORC import baidu_identify_text
import json
from config import SAVE_PATH, Record_PATH
from start_exe_tool import run_exe
from shutil import copyfile


# 读取图像
def cv_imread(file_path):
    cv_img = cv.imdecode(np.fromfile(file_path, dtype=np.uint8), cv.IMREAD_COLOR)
    return cv_img


def move_win():
    """进入登录后界面，移动窗口界面至指定位置:左上角(0，0)右下角(1100,1000)"""
    view_handle = auto_FindWindow('Qt5QWindowIcon', 'TLIAS客户端')
    win32gui.SetWindowPos(view_handle, win32con.HWND_TOPMOST, 0, 0, 1100, 1000, win32con.SWP_SHOWWINDOW)


def path_if_exist(path, build=False):
    """
    功能1：判断目录或文件是否存在
    功能2：若不存在是否递归创建该目录
    :param path: 绝对目录或相对目录  示例：'E:\\Desktop\\Auto_SR\venv' 或 '.\\venv'
    :param build: 为True时，若目录或文件不存在会递归创建目录
    :return:
    """
    result = os.path.exists(path)
    # 如果目录或文件不存在且build=True
    if build and (not result):
        os.makedirs(path)
        # print(f'已创建不存在目录{path}')
    elif (not result) and (not build):
        # print(f'不存在且未主动创建目录{path}')
        pass
    else:
        # print(f'存在目录或文件：{path}')
        return True


def check_course2(course1, course2_path):
    """
    再次确认该课程的2级课程名是否正确,
    若正确，返回1
    若不正确，重进1级课程，并进入目标课程2级课程
    :return:
    """
    # 获得句柄
    view_handle = auto_FindWindow('Qt5QWindowIcon', 'TLIAS客户端')
    point = find_picture(course2_path, view_handle)
    course2_name = os.path.basename(course2_path)[:-4]
    if not len(point):
        print(f'当前不是【{course2_name}】课程，开始切换')
        # 获得返回2级课程目录按钮的坐标
        point = find_picture(r'capture\返回2级课程目录按钮.png', view_handle)
        # 如果找到该按钮
        if point:
            mouse_left_click(point[0][0], point[0][1], 2)
        # 点击1级课程
        clect_course(course1)
        click_into_course2(course2_path)
    else:
        return 1


def into_play():
    # 设置播放器
    video_handle = auto_FindWindow('Qt5QWindow', '播放器')
    flag_1 = 'mouse'
    while True:
        # 播放视频窗口最前端显示
        # win32gui.SetWindowPos(video_handle, win32con.HWND_TOPMOST, 0, 0, 1920, 1080, win32con.SWP_SHOWWINDOW)
        win32gui.SetForegroundWindow(video_handle)
        # 显示视频播放状态栏
        mouse_move(1919, 1060)
        try:
            result = find_picture(r'capture\视频最大化时的播放按钮.png', video_handle, (153, 1051, 170, 1072), times=2, t=0.95)
            # 如果没播放
            if result:
                if flag_1 == 'mouse':
                    # 鼠标点击一下开始播放视频
                    mouse_left_click(1919, 1060, 1)
                    flag_1 = 'space'
                    time.sleep(1)
                elif flag_1 == 'space':
                    # 按一下空格开始播放视频
                    key_even('spacebar')
                    flag_1 = 'error'
                    time.sleep(1)
                elif flag_1 == 'error':
                    raise Exception('视频最大化后，无论按鼠标还是按空格都无法播放视频')
            if not result:
                mouse_move(1919, 600)
                break
        except Exception:
            print('检测视频是否最大化失败')
            break


def Screen_recording(cur_img_h, hwnd, save_path_course3, course4_text, id, cur_img_path):
    """
    course4录屏操作
    :return:
    :param cur_img_h: 当前下载课程中心在屏幕中的高度
    :param hwnd: 当前黑马播放器窗口句柄，每次启动都不同
    :param save_path_course3: 视频保存的目录 示例：'G:\下载\黑马视频\拓展课程\python运维开发\预习-day01-linux基础\'
    :param course4_text: 课程4的标题
    :param id: 该课程在该3级课程的序号
    :param cur_img_path: 准备播放的课程图片路径
    :return: 无返回值

    """
    flag = False
    rename = None
    course4_point = None
    record_error = 0
    # 读取相关图像到内存
    back_button_img = cv_imread(r'capture\视频后退键.png')
    pause_point_img = cv_imread(r'capture\视频暂停键.png')
    video_start_status_img = cv_imread(r'capture\视频00点状态.png')
    pause_status_img = cv_imread(r'capture\视频暂停状态.png')
    max_video_img = cv_imread(r'capture\视频最大化按钮.png')
    video_over_img = cv_imread(r'capture\视频结束后图片.png')

    # 获取course4_img的位置
    course4_point = find_picture(cur_img_path, hwnd,one_point=False)
    if course4_point:
        # 若匹配出多个目标，选出真实的目标
        for p in course4_point:
            abs_value = abs(p[1] - cur_img_h)
            if abs_value < 12:
                course4_point = p
                break
    if not course4_point:
        print('获取目标图像失败，终止程序')
        exit()

    while True:
        mouse_left_click(course4_point[0], course4_point[1], 2)
        time.sleep(2)
        pause_point = find_picture(pause_point_img, hwnd, num_storey=2, tpl_is_memory=True)
        back_button_point = find_picture(back_button_img, hwnd, tpl_is_memory=True)
        # 若发现后退键、暂停键，说明视频已经播放，跳出该循环
        if back_button_point and pause_point:
            break
    # 视频最大化准备
    # 若录像失败则无限循环，直到成功
    video_recording_success = False
    while not video_recording_success:
        video_max_prepare = False
        pause_num = 0
        while not video_max_prepare:
            pause_point = find_picture(pause_point_img, hwnd, num_storey=2, tpl_is_memory=True)
            if pause_point:
                while True:
                    mouse_left_click(back_button_point[0][0], back_button_point[0][1], 3)
                    video_start_status = find_picture(video_start_status_img, hwnd, num_storey=2, tpl_is_memory=True,
                                                      t=0.95)
                    # 如果视频到起始状态
                    if video_start_status:
                        break
                mouse_left_click(back_button_point[0][0], back_button_point[0][1], 1)
                mouse_left_click(200, 700, 1)
                pause_status = find_picture(pause_status_img, hwnd, num_storey=2, tpl_is_memory=True)
                time.sleep(1)
                if pause_status:
                    max_video = find_picture(max_video_img, hwnd, num_storey=2, tpl_is_memory=True)
                    mouse_left_click(max_video[0][0], max_video[0][1], 1)
                    # 视频最大化成功后停止循环
                    video_max_prepare = True
            # 没发现暂停键,说明视频是暂停状态
            else:
                play_point = find_picture(pause_status_img, hwnd, num_storey=2, tpl_is_memory=True)
                mouse_left_click(play_point[0][0], play_point[0][1], 1)
                # 点击播放键次数
                pause_num += 1
                time.sleep(2)
                print(f'第{pause_num}次查找暂停键失败！')
                if pause_num == 5:
                    bgr_img = window_capture(None, (0, 0, 1920, 1080))
                    cv.imwrite(r'Bug\find_pause_key_fail.png', bgr_img)
                    print('查找暂停键失败,已输出失败截图至Bug目录！')
                    exit()
        mouse_move(1919, 800)
        key_even('F2')
        time.sleep(0.5)
        mouse_left_click(1919, 800, 1)
        # key_even('spacebar') 空格有时不灵
        # todo 修改此处测试
        # 不断循环匹配视频结束后的图标，匹配到后，结束录制，按Esc退出全屏
        # 获得播放器句柄
        video_handle = auto_FindWindow('Qt5QWindow', '播放器')
        # 确定视频正在播放
        into_play()
        while True:
            try:
                # 检测视频是否播放结束
                video_over = find_picture(video_over_img, video_handle, num_storey=2, tpl_is_memory=True)
                # 发现视频已录制结束
                if video_over:
                    key_even('F2')
                    key_even('spacebar')
                    key_even('esc')
                    flag = False
                    time.sleep(2)
                    break
            except:
                # 结束视频录制
                key_even('F2')
                while True:
                    word = input('检测到已退出黑马播放器！！\n是否需要继续录制？\n请输入Y或者N:\n')
                    if (word == 'Y') or (word == 'y'):
                        print('注意：'
                              '若需要继续录制，请不要点击、移动、最小化黑马播放器!!!\n'
                              '若您操作不当导致继续录制失败，请重启本程序，选择断点续录！！！\n'
                              '有单身的小姐姐愿意和我交个朋友嘛~~(*￣∇￣*)'
                              )
                        input('准备好后请再次输入Y\n')
                        print('开始继续录制！请不要操作键鼠！开启中...')
                        # 开启重新循环标志
                        flag = True
                        break

                    if (word == 'N') or (word == 'n'):
                        print("已退出程序！")
                        exit()
                if flag:
                    # 重新继续录制
                    break
        if flag:
            # 重新继续录制
            continue
        # # todo 修改开始
        # time.sleep(5)
        # # 结束视频录制
        # key_even('F2')
        # # 按空格暂停视频
        # key_even('spacebar')
        # # 按Esc退出全屏
        # key_even('esc')
        # time.sleep(2)
        # todo 修改结束
        # 获得录屏软件，录屏后自动保存视频文件的路径
        save_video_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(save_path_course3)))) + '\\'
        list1 = os.listdir(save_video_path)
        mp4_new = (str(), 0)
        for f in list1:
            if f[-4:] == '.mp4':
                path = save_video_path + f
                # 返回该文件的最后修改时间
                file_time = os.path.getmtime(path)
                if file_time > mp4_new[1]:
                    mp4_new = (path, file_time)
        # 如果没发现mp4文件
        if not mp4_new[0]:
            assert 0, f'没有找到录制的mp4文件，请确认录屏软件保存目录是否在{SAVE_PATH}'
        # 输出示例：('G:\\下载\\黑马视频\\录制_2020_06_24_14_18_53_265.mp4', 1592979536.4101696)
        # print(mp4_new)
        # 设定重命名该视频的名称
        rename = f'{id:0>2}' + '_' + course4_text + '.mp4'
        # 核对是否有同名文件,若有直接删除
        if os.path.exists(save_path_course3 + rename):
            os.remove(save_path_course3 + rename)
            print(f'发现同名文件{rename}，已删除！')
            time.sleep(1)
        try:
            os.rename(mp4_new[0], save_path_course3 + rename)
            print(f'{rename}已下载完毕！')
            video_recording_success = True
        except:
            # 自录软件状态错误，结束视频录制，重新录制
            key_even('F2')
            print('自录软件状态错误,重新开始录制')
            record_error += 1
            if record_error == 2:
                print('自录软件已2次错误且调整失败，即将重启录屏软件！')
                run_exe(Record_PATH)  # 启动录屏软件客户端
                # 等待录屏软件重启完毕
                time.sleep(20)
                print('录屏软件客户端已重启！')


def get_course_img_text(point):
    """
    根据课程的坐标点获得目标课程的课程图片、翻译文本、课程是蓝点还是灰圆
    :param point: 当前关注的坐标点
    :return: 图片和文本元祖 示例：(target_img, target_text,'circle')
    """
    img_w = 420
    img_h = 20
    target_img = window_capture(0, (point[0], point[1] - 10, img_w, img_h))
    # 返回该图片的文字内容
    target_text = baidu_identify_text(target_img)
    # 判断识别出的文字作为变量名称是否非法
    for value in ':*?"<>|':
        if value in target_text:
            # 替换非法字符串为下划线:_
            target_text = target_text.replace(value, '_')
    if '时长' in target_text:
        num = target_text.rfind('时')
        target_text = target_text[:num]
        return (target_img, target_text)
    # cv.imshow('target_img',target_img)
    # cv.waitKey(-1)
    # cv.destroyAllWindows()
    # print(target_text)
    return (target_img, target_text)


def move_top(cur_img):
    """
    移动当前关注的3级或4级课程到顶点
    :param ：cur_img_path: 当前关注的3级或4级课程截图路径
    :return: 返回当前关注的课程最终实际高度
    """
    view_handle = None
    h = 5000
    num = 1
    # 读取相关图像到内存
    top_point_img = cv_imread(r'capture\获取置顶高度图片.png')
    while num:
        view_handle = auto_FindWindow('Qt5QWindowIcon', 'TLIAS客户端')
        top_point_h = find_picture(top_point_img, view_handle, tpl_is_memory=True)[0][1]
        cur_img_h = find_picture(cur_img, view_handle, num_storey=2, tpl_is_memory=True, one_point=False, t=0.95)[0][1]
        置顶移动的高度 = top_point_h - cur_img_h
        # print(f'top_point_h:{top_point_h}\ncourse3_h:{cur_img_h}')
        if (置顶移动的高度 < -20) and (h != 置顶移动的高度):
            # print(f'置顶移动的高度:{置顶移动的高度}')
            mouse_wheel(1074, 600, 置顶移动的高度)
            h = 置顶移动的高度
        elif (置顶移动的高度 < -20) and (h == 置顶移动的高度):
            # print(f'置顶移动失败！')
            # 1次置顶失败则退出循环
            num -= 1
        # 既不置顶失败，也不达到继续置顶要求，此时退出置顶循环
        else:
            break
    # 当前图片所在高度
    cur_img_h = find_picture(cur_img, view_handle, num_storey=2, tpl_is_memory=True, one_point=False, t=0.95)[0][
        1]
    return cur_img_h


def match_nearst_point(cur_img_path, cur_img_h, hwnd):
    """
    返回离cur_img_path图像最近的蓝点、灰圆
    :param cur_img_path: 对比图片的相对路径 示例：r'capture\course3.png'
    :param cur_img_h: 当前关注图片的实际高度
    :param hwnd: 黑马窗口句柄
    :return: 返回最近的点 示例：((588, 252), 'blue')
    """
    # 若找目标下方的点失败，则循环3次查找
    nearst_point = None
    num = 3
    while num:
        nearst_point = None
        nearst_blue = None
        nearst_circle = None
        # 获取所有蓝点
        blue = r'capture\4级课程蓝点.png'
        blue_list = find_picture(blue, hwnd, one_point=False)

        if blue_list:
            for point in blue_list:
                if point[1] > (cur_img_h + 10):
                    # 找到离关注图像最近的蓝点的中心坐标
                    nearst_blue = point
                    break

        # 获取所有灰圆高度
        circle = r'capture\3级课程灰圆.png'
        circle_list = find_picture(circle, hwnd, one_point=False)
        if circle_list:
            for point in circle_list:
                if point[1] > (cur_img_h + 10):
                    # 找到离关注图像最近的灰圆的中心坐标
                    nearst_circle = point
                    break

        # 比较2个最近点，输出最近的点
        # 2个点都有
        if nearst_blue and nearst_circle:
            if nearst_blue[1] > nearst_circle[1]:
                nearst_point = (nearst_circle, 'circle')
            if nearst_blue[1] < nearst_circle[1]:
                nearst_point = (nearst_blue, 'blue')
            break
            # 只有blue
        elif nearst_blue and not nearst_circle:
            nearst_point = (nearst_blue, 'blue')
            break
            # 只有circle
        elif not nearst_blue and nearst_circle:
            nearst_point = (nearst_circle, 'circle')
            break
        else:
            # print(f'查找图片{cur_img_path}下方对近的点失败,返回值为None!')
            nearst_point = (None, None)
            num -= 1
            time.sleep(1)

    return nearst_point


def title_location(course1, course2_path, save_path_course2, break_point=False):
    """
    开始录屏
    :param course1: 1级课程名 示例：'拓展课程'
    :param course2_path: 自选2级课程的图片路径  示例: 'capture/outward_bound_course/python运维开发.png'
    :param save_path_course2: 二级课程保存目录 示例：'G:\下载\黑马视频\拓展课程\python运维开发'
    :return:
    """
    course3_pass = None
    view_handle = auto_FindWindow('Qt5QWindowIcon', 'TLIAS客户端')
    path_if_exist(save_path_course2, True)
    time.sleep(2)
    whell = find_picture(r'capture\4级课程滚动条.png', view_handle, num_storey=2, t=0.95)
    if whell:
        time.sleep(1)
        print('已拖动滚动条到顶部')
        mouse_left_click_move(whell[0][0], whell[0][1], whell[0][0], 80)

    time.sleep(1)
    cur_img_path = r'capture\获取置顶高度图片.png'
    cur_img_h = find_picture(r'capture\获取置顶高度图片.png', view_handle)[0][1]
    # print('course2.png保存成功！')
    id = 0
    # 申明变量
    save_path_course3 = str()
    # 无限循环
    while True:
        # 再次确认窗口大小是否正常
        move_win()
        check_course2(course1, course2_path)
        nearst_point = match_nearst_point(cur_img_path, cur_img_h, view_handle)
        # print(f'nearst_point:{nearst_point}')
        # 激活了断点续传
        if break_point:
            nearst_point = (1, 'blue')
        # 如果灰圆最近：
        if nearst_point[1] == 'circle':
            # 找到此灰圆并截图保存为course3
            course3_info = get_course_img_text(nearst_point[0])
            cv.imwrite(r'capture/memory_archive\course3_pass.png', course3_info[0])
            cur_img_path = r'capture/memory_archive\course3_pass.png'
            # 把当前图片置顶
            cur_img_h = move_top(course3_info[0])
            save_path_course3 = save_path_course2 + '\\' + course3_info[1] + '\\'
            # 创建存放3级课程存储目录
            path_if_exist(save_path_course3, True)
            id = 0
        # 如果蓝点最近：
        elif nearst_point[1] == 'blue':
            # 激活了断点续传
            if break_point:
                # 读取断点资料
                with open(r'capture/memory_archive\break_point_recording', 'r', encoding='utf8') as f:
                    json_info = f.read()
                dict_info = json.loads(json_info)
                # 取出相应变量的值
                course1 = dict_info['course1']
                course2_path = dict_info['course2_path']
                save_path_course2 = dict_info['save_path_course2']
                save_path_course3 = dict_info['save_path_course3']
                course4_text = dict_info['course4_text']
                id = dict_info['id']
                cur_img_path = dict_info['cur_img_path']
                # 找到并置顶course3
                course3_img = cv_imread(r'capture/memory_archive/course3.png')
                while True:
                    course3_point = find_picture(course3_img, view_handle, tpl_is_memory=True,t=0.97)
                    if course3_point:
                        move_top(course3_img)
                        break
                    # 如果没找到course3,鼠标向下滚动
                    else:
                        mouse_wheel(800, 600, -500)
                # 找到并置顶course4
                course4_img = cv_imread(r'capture/memory_archive\course4.png')
                while True:
                    course4_point = find_picture(course4_img, view_handle, num_storey=3, t=0.95, tpl_is_memory=True)
                    if course4_point:
                        cur_img_h = move_top(course4_img)
                        break
                    # 如果没找到course3,鼠标向下滚动
                    else:
                        mouse_wheel(800, 600, -500)
                # 获取course4的坐标传给Screen_recording()开始录屏
                Screen_recording(cur_img_h, view_handle, save_path_course3, course4_text, id,
                                 r'capture/memory_archive\course4.png')
                # 关闭断点续传
                break_point = False

            # 断点续传未激活
            else:
                # course3的录制的第id个课程
                id += 1
                course4_info = get_course_img_text(nearst_point[0])
                course4_text = course4_info[1]
                cur_img_path = r'capture/memory_archive\course4.png'
                cur_img_h = move_top(course4_info[0])
                dict_info = {'course1': course1,
                             'course2_path': course2_path,
                             'save_path_course2': save_path_course2,
                             'save_path_course3': save_path_course3,
                             'course4_text': course4_text,
                             'id': id,
                             'cur_img_path': r'capture\memory_archive\course4.png'}
                json_info = json.dumps(dict_info)
                with open(r'capture/memory_archive\break_point_recording', 'w', encoding='utf8') as f:
                    f.write(json_info)
                course2_img = cv_imread(course2_path)
                cv.imwrite(r'capture/memory_archive\course2.png', course2_img)
                os.popen(r'copy capture\memory_archive\course3_pass.png capture\memory_archive\course3.png')
                cv.imwrite(r'capture/memory_archive\course4.png', course4_info[0])
                Screen_recording(cur_img_h, view_handle, save_path_course3, course4_text, id,
                                 r'capture/memory_archive\course4.png')

        # 没有蓝点和灰圆
        else:
            course2_name = os.path.basename(course2_path)[:-4]
            print(f'{course2_name}课程已全部下载结束！♪(＾∀＾●)ﾉ')
            # 添加已course2下载完成标记
            dst_scr = save_path_course2 + '\\' + 'course2.png'
            os.popen(r'copy capture\memory_archive\course2.png ' + dst_scr)
            time.sleep(1)
            # 删除断点续录记忆
            list_imgs = [r'capture\memory_archive\course4.png', r'capture\memory_archive\course3.png',
                         r'capture\memory_archive\course2.png',
                         r'capture\memory_archive\break_point_recording']
            for file in list_imgs:
                if path_if_exist(file):
                    os.remove(file)
            exit_point = find_picture(r'capture\返回2级课程目录按钮.png', view_handle, )
            mouse_left_click(exit_point[0][0], exit_point[0][1], 2)
            break


if __name__ == '__main__':
    pass
    # title_location('拓展课程', 'capture\outward_bound_course\django美多商品秒杀.png', 'G:\下载\黑马视频\拓展课程\django美多商品秒杀')
