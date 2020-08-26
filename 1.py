# -*- coding: utf-8 -*-
# @Time    : 2020/8/25 5:35
# @Author  : LY
import win32con
import win32gui
import os


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
    hightlight_old_window()
