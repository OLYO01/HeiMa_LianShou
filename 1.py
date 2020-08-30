# -*- coding: utf-8 -*-
# @Time    : 2020/8/25 5:35
# @Author  : LY
import win32con
import win32gui
import os, re
from config import SAVE_PATH, Custom_Settings


def recording_config_init():
    # 获得配置文件路径
    # C:\Users\LY\AppData\Local\Temp\oCam\oCam\Config.ini
    recording_config_path = os.environ['TEMP'] + r'\oCam\oCam\Config.ini'
    # 把window_path转换成符合当前系统的分隔符，2个替换有一个会生效
    recording_config_path = recording_config_path.replace('/', os.sep)
    recording_config_path = recording_config_path.replace('\\', os.sep)

    def modify_copy_config(copy_origin_path):
        # 根据config.py生成基础模板配置文件
        # 读取基本模板配置文件
        with open(copy_origin_path, 'r', encoding='gbk') as file:
            unicode_data = file.read()
        # 替换的正则表达式
        re_str = r'lbledtOutputPath=(.*)'
        # 替换的字符串
        new_data = 'lbledtOutputPath=' + SAVE_PATH
        # 开始替换
        new_config_data = re.sub(re_str, new_data, unicode_data)
        # 创建视频配置文件并根据config.py写入最新配置
        with open(recording_config_path, 'w', encoding='gbk')as file:
            file.write(new_config_data)

    # 如果没有配置文件，复制粘贴模板配置文件
    if not os.path.exists(recording_config_path):
        path = 'oCam\Config.ini'
        modify_copy_config(path)
        print('录屏配置模块初始化成功...')
    # 如果有配置文件，查看录屏放置地址是否默认地址
    else:
        # 读取当前录屏配置文件
        with open(recording_config_path, 'r', encoding='gbk') as file:
            unicode_data2 = file.read()
        # 查找的正则表达式
        re_str2 = r'lbledtOutputPath=(.*)'
        result = re.search(re_str2, unicode_data2).group(1)
        # 若不是config.py文件下载地址，复制粘贴默认配置文件
        if result != SAVE_PATH:
            if Custom_Settings == True:
                modify_copy_config(recording_config_path)
                print('录屏配置模块已完成录屏保存地址修改...')
            else:
                path = 'oCam\Config.ini'
                modify_copy_config(path)
                print('录屏配置模块重新初始化成功...')
        # 若是config.py文件下载地址，直接启动录屏文件
        else:
            print('录屏配置模块自检正常...')


def a1():
    recording_config_path = 'G:\下载\Config1.ini'
    with open(recording_config_path, 'r', encoding='GBK') as file:
        unicode_data2 = file.read()
    print(unicode_data2)
    # unicode_data2 = 'gbMouseCursorSize=100\nlbledtOutputPath=G:\下载\黑马视频2\nledtFileName=<Prefix>_<YYYY_MM_DD_HH_NN_SS_Z>'
    # 查找的正则表达式
    re_str2 = r'lbledtOutputPath=(.*)'
    # print(f'替换后的字符串: {new_config_data}')
    result = re.search(re_str2, unicode_data2)
    if result:
        result = result.group(1)
        print(result)
    else:
        print('匹配下载目录字符串失败')


def a2():
    with open(r'G:\下载\lala1.txt', 'r') as f:
        f.read()


if __name__ == '__main__':
    recording_config_init()
    # a1()
