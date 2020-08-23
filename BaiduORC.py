# -*- coding: utf-8 -*-
# @Time    : 2020/4/29 11:47
# @Author  : LY

from aip import AipOcr
import cv2 as cv
import numpy as np

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def baidu_identify_text(png_img=None,png_file_path=None):
    APP_ID = '19750434'
    API_KEY = '60SeispGwawsyPNXoEm6pqtS'
    SECRET_KEY = '0Sn43Ona3vF79veUpRXOnTa2j9AurQld'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    options = {}
    options["detect_direction"] = "true"
    options["probability"] = "False"

    if png_file_path and (not png_img):
        png_img = cv.imdecode(np.fromfile(png_file_path, dtype=np.uint8), cv.IMREAD_COLOR)
    bytes_picture = cv.imencode('.png', png_img)[1].tobytes()

    """ 带参数调用通用文字识别（高精度版） """
    result = client.basicAccurate(bytes_picture, options)
    identify_text = result['words_result'][0]['words']
    return identify_text


if __name__ == '__main__':
    result = baidu_identify_text(None,r'capture\course4.png')
    print(result)
