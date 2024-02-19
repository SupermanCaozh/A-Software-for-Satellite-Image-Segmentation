'''
    -*- coding: utf-8 -*-
    EGWOSIS MAIN PROGRAM
    
'''

import sys
import os
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import xlwt
import BaseFunctions


def cv_imread(file_path):
    # 修改cv2读取路径问题
    f = lambda x: sum([1 if u'\u4e00' <= i <= u'\u9fff' else 0 for i in x]) > 0
    if f(file_path):
        cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    else:
        cv_img = cv2.imread(file_path)
    return cv_img


def cv_imwrite(img, save_dir):
    # 修改cv2存储路径问题
    f = lambda x: sum([1 if u'\u4e00' <= i <= u'\u9fff' else 0 for i in x]) > 0
    if f(save_dir):
        cv2.imencode('.png', img)[1].tofile(save_dir)
    else:
        cv2.imwrite(save_dir, img)


class Ui_MainWindow(object):
    ...
    # Please contact the author for the right to use and the completed version of codes.

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # 创建一个QApplication
    MainWindow = QtWidgets.QMainWindow()  # 创建一个QMainWindow
    ui = Ui_MainWindow()  # Ui_MainWindow()类的实例化对象
    ui.setupUi(MainWindow)  # 执行setupUi方法
    MainWindow.show()  # 显示QMainWindow
    sys.exit(app.exec_())
