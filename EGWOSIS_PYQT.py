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
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowIcon(QtGui.QIcon(":\icon.ico"))  # 设置图标
        MainWindow.setFixedSize(1460, 850)  # 固定窗口大小

        self.centralwidget = QtWidgets.QWidget(MainWindow)  # 中心布局组件
        self.centralwidget.setObjectName("centralwidget")

        font = QtGui.QFont()
        font.setFamily("Haettenschweiler")  # 字体类型
        font.setPointSize(24)  # 字体大小

        self.label_TOI = QtWidgets.QLabel(self.centralwidget)  # Text: 'The Original Imagery'
        self.label_TOI.setGeometry(QtCore.QRect(160, 30, 301, 51))
        self.label_TOI.setFont(font)
        self.label_TOI.setObjectName("label_TOI")

        self.label_TSI = QtWidgets.QLabel(self.centralwidget)  # Text: 'The Segmented Imagery'
        self.label_TSI.setGeometry(QtCore.QRect(730, 30, 381, 51))
        self.label_TSI.setFont(font)
        self.label_TSI.setObjectName("label_TSI")

        self.layoutWidget_originalimagery = QtWidgets.QWidget(self.centralwidget)  # The Original Imagery的布局组件
        self.layoutWidget_originalimagery.setGeometry(QtCore.QRect(30, 90, 551, 421))
        self.layoutWidget_originalimagery.setObjectName("layoutWidget_originalimagery")

        self.gridLayout_originalimagery = QtWidgets.QGridLayout(
            self.layoutWidget_originalimagery)  # 对layoutWidget_originalimagery进行网格布局
        self.gridLayout_originalimagery.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_originalimagery.setObjectName("gridLayout_originalimagery")

        self.graphicsView_original = QtWidgets.QGraphicsView(
            self.layoutWidget_originalimagery)  # The Original Imagery 展示窗口
        self.graphicsView_original.setObjectName("graphicsView_original")
        self.gridLayout_originalimagery.addWidget(self.graphicsView_original, 0, 0, 1, 1)
        self.scene_original = QtWidgets.QGraphicsScene()  # 创建画布
        self.graphicsView_original.setScene(self.scene_original)  # 把画布添加到The Original Imagery 展示窗口
        self.graphicsView_original.show()  # 显示画布

        self.pushButton_II = QtWidgets.QPushButton(self.layoutWidget_originalimagery)  # 设置按钮Import Imagery
        self.pushButton_II.setObjectName("pushButton_II")
        self.gridLayout_originalimagery.addWidget(self.pushButton_II, 1, 0, 1, 1)
        self.pushButton_II.clicked.connect(self.Import_Imagery)

        self.layoutWidget_function = QtWidgets.QWidget(self.centralwidget)  # objective function的布局组件
        self.layoutWidget_function.setGeometry(QtCore.QRect(30, 640, 518, 23))
        self.layoutWidget_function.setObjectName("layoutWidget_function")

        self.horizontalLayout_function = QtWidgets.QHBoxLayout(
            self.layoutWidget_function)  # 对layoutWidget_function进行水平布局
        self.horizontalLayout_function.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_function.setObjectName("horizontalLayout_function")

        font2 = QtGui.QFont()
        font2.setPointSize(8)  # 字体大小
        self.label_function = QtWidgets.QLabel(self.layoutWidget_function)  # Text: 'Choose the objective function:'
        self.label_function.setObjectName("label_function")
        self.label_function.setFont(font2)
        self.horizontalLayout_function.addWidget(self.label_function)

        self.comboBox_function = QtWidgets.QComboBox(self.layoutWidget_function)  # 设置function复选框
        self.comboBox_function.setEditable(False)  # 设置复选框可编辑
        self.comboBox_function.setMaxVisibleItems(3)  # 列最大可见数
        self.comboBox_function.setObjectName("comboBox_function")
        for i in range(3):
            self.comboBox_function.addItem("")  # 添加可选项
        self.horizontalLayout_function.addWidget(self.comboBox_function)

        self.graphicsView_segmented = QtWidgets.QGraphicsView(self.centralwidget)  # The Segmented Imagery 展示窗口
        self.graphicsView_segmented.setGeometry(QtCore.QRect(610, 90, 561, 411))
        self.graphicsView_segmented.setObjectName("graphicsView_segmented")
        self.scene_segmented = QtWidgets.QGraphicsScene()  # 创建画布
        self.graphicsView_segmented.setScene(self.scene_segmented)  # 把画布添加到The Segmented Imagery 展示窗口
        self.graphicsView_segmented.show()  # 显示画布

        self.graphicsView_R = QtWidgets.QGraphicsView(self.centralwidget)  # R Image 展示窗口
        self.graphicsView_R.setGeometry(QtCore.QRect(1180, 90, 251, 131))
        self.graphicsView_R.setObjectName("graphicsView_R")
        self.scene_R = QtWidgets.QGraphicsScene()  # 创建画布
        self.graphicsView_R.setScene(self.scene_R)  # 把画布添加到R Image 展示窗口
        self.graphicsView_R.show()  # 显示画布

        self.graphicsView_G = QtWidgets.QGraphicsView(self.centralwidget)  # G Image 展示窗口
        self.graphicsView_G.setGeometry(QtCore.QRect(1180, 230, 251, 131))
        self.graphicsView_G.setObjectName("graphicsView_G")
        self.scene_G = QtWidgets.QGraphicsScene()  # 创建画布
        self.graphicsView_G.setScene(self.scene_G)  # 把画布添加到G Image 展示窗口
        self.graphicsView_G.show()  # 显示画布

        self.graphicsView_B = QtWidgets.QGraphicsView(self.centralwidget)  # B Image 展示窗口
        self.graphicsView_B.setGeometry(QtCore.QRect(1180, 370, 251, 131))
        self.graphicsView_B.setObjectName("graphicsView_B")
        self.scene_B = QtWidgets.QGraphicsScene()  # 创建画布
        self.graphicsView_B.setScene(self.scene_B)  # 把画布添加到B Image 展示窗口
        self.graphicsView_B.show()  # 显示画布

        self.layoutWidget_partitions = QtWidgets.QWidget(self.centralwidget)  # 三个partitions选择部分的位置组件
        self.layoutWidget_partitions.setGeometry(QtCore.QRect(30, 520, 551, 101))
        self.layoutWidget_partitions.setObjectName("layoutWidget_partitions")

        self.gridLayout_partitions = QtWidgets.QGridLayout(
            self.layoutWidget_partitions)  # 对layoutWidget_partitions进行网格布局
        self.gridLayout_partitions.setContentsMargins(0, 0, 0, 0)  # 设置内容边距(左,上,右,下)
        self.gridLayout_partitions.setObjectName("gridLayout_partitions")

        self.label_partitions_R = QtWidgets.QLabel(
            self.layoutWidget_partitions)  # Text: 'How many partitions of the Red channel image do you want?'
        self.label_partitions_R.setObjectName("label_partitions_R")
        self.label_partitions_R.setFont(font2)
        self.gridLayout_partitions.addWidget(self.label_partitions_R, 0, 0, 1, 1)

        self.spinBox_R = QtWidgets.QSpinBox(self.layoutWidget_partitions)  # R的partitions选择框
        self.spinBox_R.setMinimum(2)
        self.spinBox_R.setMaximum(100)
        self.spinBox_R.setObjectName("spinBox_R")
        self.gridLayout_partitions.addWidget(self.spinBox_R, 0, 1, 1, 1)

        self.label_partitions_G = QtWidgets.QLabel(
            self.layoutWidget_partitions)  # Text: 'How many partitions of the Green channel image do you want?'
        self.label_partitions_G.setObjectName("label_G")
        self.label_partitions_G.setFont(font2)
        self.gridLayout_partitions.addWidget(self.label_partitions_G, 1, 0, 1, 1)

        self.spinBox_G = QtWidgets.QSpinBox(self.layoutWidget_partitions)  # G的partitions选择框
        self.spinBox_G.setMinimum(2)
        self.spinBox_G.setMaximum(100)
        self.spinBox_G.setObjectName("spinBox_G")
        self.gridLayout_partitions.addWidget(self.spinBox_G, 1, 1, 1, 1)

        self.label_partitions_B = QtWidgets.QLabel(
            self.layoutWidget_partitions)  # Text: 'How many partitions of the Blue channel image do you want?'
        self.label_partitions_B.setObjectName("label_partitions_B")
        self.label_partitions_B.setFont(font2)
        self.gridLayout_partitions.addWidget(self.label_partitions_B, 2, 0, 1, 1)

        self.spinBox_B = QtWidgets.QSpinBox(self.layoutWidget_partitions)  # B的partitions选择框
        self.spinBox_B.setMinimum(2)
        self.spinBox_B.setMaximum(100)
        self.spinBox_B.setObjectName("spinBox_B")
        self.gridLayout_partitions.addWidget(self.spinBox_B, 2, 1, 1, 1)

        self.layoutWidget_progressbar = QtWidgets.QWidget(self.centralwidget)  # Start Button 和 progressbar 的布局组件
        self.layoutWidget_progressbar.setGeometry(QtCore.QRect(30, 680, 551, 101))
        self.layoutWidget_progressbar.setObjectName("layoutWidget_progressbar")

        self.gridLayout_progressbar = QtWidgets.QGridLayout(
            self.layoutWidget_progressbar)  # 对layoutWidget_progressbar进行网格布局
        self.gridLayout_progressbar.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_progressbar.setObjectName("gridLayout_progressbar")

        self.progressBar = QtWidgets.QProgressBar(self.layoutWidget_progressbar)  # 设置进度条
        self.progressBar.setProperty("value", 0)  # 初始位置
        self.progressBar.setObjectName("progressBar")

        self.gridLayout_progressbar.addWidget(self.progressBar, 1, 1, 1, 1)  # 设置按钮Start Segmentation
        self.pushButton_SS = QtWidgets.QPushButton(self.layoutWidget_progressbar)
        self.pushButton_SS.setObjectName("pushButton_SS")
        self.gridLayout_progressbar.addWidget(self.pushButton_SS, 1, 0, 1, 1)
        self.pushButton_SS.clicked.connect(self.start)

        self.label_note = QtWidgets.QLabel(self.layoutWidget_progressbar)  # Note 内容
        self.label_note.setObjectName("label_note")
        self.label_note.setStyleSheet("color:red")
        self.label_note.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout_progressbar.addWidget(self.label_note, 0, 0, 1, 2)

        self.layoutWidget_table = QtWidgets.QWidget(self.centralwidget)  # 表格的布局组件
        self.layoutWidget_table.setGeometry(QtCore.QRect(670, 550, 731, 229))
        self.layoutWidget_table.setObjectName("layoutWidget_table")

        self.gridLayout_table = QtWidgets.QGridLayout(self.layoutWidget_table)  # 表格的网格布局
        self.gridLayout_table.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_table.setObjectName("gridLayout_table")

        self.tableWidget = QtWidgets.QTableWidget(self.layoutWidget_table)  # 设置表格
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setMaximumSize(QtCore.QSize(821, 16777215))  # 表格最大尺寸
        self.tableWidget.setShowGrid(True)  # 显示网格线
        self.tableWidget.setStyleSheet("QHeaderView::section{background:lightgrey;color: black;}")  # 设置表头背景颜色
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)  # 无法选中
        self.tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)  # 固定行高
        self.tableWidget.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)  # 设置滚动条按像素滚动
        self.tableWidget.setColumnCount(10)  # 设置列数
        self.tableWidget.setRowCount(3)  # 设置行数
        for column in range(10):
            self.tableWidget.setColumnWidth(column, 120)  # 设置列宽
        for row in range(3):
            self.tableWidget.setRowHeight(row, 47)  # 设置行高
        self.tableWidget.setVerticalHeaderLabels(['R Channel', 'G Channel', 'B Channel'])  # 设置竖直表头标签
        self.gridLayout_table.addWidget(self.tableWidget, 0, 0, 1, 2)

        self.pushButton_ERAF = QtWidgets.QPushButton(self.layoutWidget_table)  # 设置按钮 Export results as file
        self.pushButton_ERAF.setObjectName("pushButton_ERAF")
        self.gridLayout_table.addWidget(self.pushButton_ERAF, 1, 0, 1, 1)
        self.pushButton_ERAF.clicked.connect(self.export_result_as_file)

        self.pushButton_EXIT = QtWidgets.QPushButton(self.layoutWidget_table)  # 设置按钮 Exit
        self.pushButton_EXIT.setObjectName("pushButton_EXIT")
        self.gridLayout_table.addWidget(self.pushButton_EXIT, 1, 1, 1, 1)
        self.pushButton_EXIT.clicked.connect(self.exit)

        self.widget_buttons = QtWidgets.QWidget(self.centralwidget)  # 四个按钮的布局组件
        self.widget_buttons.setGeometry(QtCore.QRect(720, 510, 671, 36))
        self.widget_buttons.setObjectName("widget_buttons")

        self.horizontalLayout_buttons = QtWidgets.QHBoxLayout(self.widget_buttons)  # 对widget_buttons进行水平布局
        self.horizontalLayout_buttons.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_buttons.setObjectName("horizontalLayout_buttons")

        self.pushButton_SAF = QtWidgets.QPushButton(self.widget_buttons)  # 设置按钮save as file
        self.pushButton_SAF.setObjectName("pushButton_SAF")
        self.horizontalLayout_buttons.addWidget(self.pushButton_SAF)
        self.pushButton_SAF.clicked.connect(self.save_as_file)

        self.pushButton_SRI = QtWidgets.QPushButton(self.widget_buttons)  # 设置按钮save R image
        self.pushButton_SRI.setObjectName("pushButton_SRI")
        self.horizontalLayout_buttons.addWidget(self.pushButton_SRI)
        self.pushButton_SRI.clicked.connect(self.save_R_image)

        self.pushButton_SGI = QtWidgets.QPushButton(self.widget_buttons)  # 设置按钮save G image
        self.pushButton_SGI.setObjectName("pushButton_SGI")
        self.horizontalLayout_buttons.addWidget(self.pushButton_SGI)
        self.pushButton_SGI.clicked.connect(self.save_G_image)

        self.pushButton_SBI = QtWidgets.QPushButton(self.widget_buttons)  # 设置按钮save B image
        self.pushButton_SBI.setObjectName("pushButton_SBI")
        self.horizontalLayout_buttons.addWidget(self.pushButton_SBI)
        self.pushButton_SBI.clicked.connect(self.save_B_image)

        self.menubar = QtWidgets.QMenuBar(MainWindow)  # 设置父级菜单
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1500, 30))
        MainWindow.setMenuBar(self.menubar)  # 显示菜单
        self.menubar.setObjectName("menubar")

        self.menuFile = QtWidgets.QMenu(self.menubar)  # 子级菜单File
        self.menuFile.setObjectName("menuFile")

        self.menuExit = QtWidgets.QMenu(self.menubar)  # 子级菜单Exit
        self.menuExit.setObjectName("menuExit")

        self.actionImport_images = QtWidgets.QAction(MainWindow)  # 按钮Import Images
        self.actionImport_images.setObjectName("actionImport_images")
        self.actionImport_images.triggered.connect(self.Import_Imagery)

        # self.actionHow_to_use = QtWidgets.QAction(MainWindow)  # 按钮How to use?
        # self.actionHow_to_use.setObjectName("actionHow_to_use")

        self.actionSave_and_exit = QtWidgets.QAction(MainWindow)  # 按钮Save and exit
        self.actionSave_and_exit.setObjectName("actionSave_and_exit")
        self.actionSave_and_exit.triggered.connect(self.save_and_exit)

        self.actionExit_directly = QtWidgets.QAction(MainWindow)  # 按钮Exit directly
        self.actionExit_directly.setObjectName("actionExit_directly")
        self.actionExit_directly.triggered.connect(self.exit)

        # 添加菜单
        self.menuFile.addAction(self.actionImport_images)
        # self.menuFile.addAction(self.actionHow_to_use)
        self.menuExit.addAction(self.actionSave_and_exit)
        self.menuExit.addAction(self.actionExit_directly)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuExit.menuAction())

        MainWindow.setCentralWidget(self.centralwidget)  # 显示主窗口
        self.retranslateUi(MainWindow)  # 调用retranslateUi
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        # 设置组件标签
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "EGWOSIS"))
        self.label_TSI.setText(_translate("MainWindow", "The Segmented Imagery"))
        self.label_TOI.setText(_translate("MainWindow", "The Original Imagery"))
        self.label_partitions_R.setText(
            _translate("MainWindow", "How many partitions of the Red channel image do you want?"))
        self.label_partitions_G.setText(
            _translate("MainWindow", "How many partitions of the Green channel image do you want?"))
        self.label_partitions_B.setText(
            _translate("MainWindow", "How many partitions of the Blue channel image do you want?"))
        self.pushButton_SS.setText(_translate("MainWindow", "Start Segmentation"))
        self.label_note.setText(
            _translate("MainWindow", "*Note: The more partitions you choose, the \nlonger the programs runs!"))
        self.pushButton_II.setText(_translate("MainWindow", "Import imagery"))
        self.label_function.setText(_translate("MainWindow", "Choose the objective function:"))
        self.comboBox_function.setItemText(0, _translate("MainWindow", "Otsu\'s between-class variance"))
        self.comboBox_function.setItemText(1, _translate("MainWindow", "Kapur\'s entropy"))
        self.comboBox_function.setItemText(2, _translate("MainWindow", "Tsallis entropy"))
        self.pushButton_ERAF.setText(_translate("MainWindow", "Export results as file"))
        self.pushButton_EXIT.setText(_translate("MainWindow", "Exit"))
        self.pushButton_SAF.setText(_translate("MainWindow", "Save as file"))
        self.pushButton_SRI.setText(_translate("MainWindow", "Save R image"))
        self.pushButton_SGI.setText(_translate("MainWindow", "Save G image"))
        self.pushButton_SBI.setText(_translate("MainWindow", "Save B image"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuExit.setTitle(_translate("MainWindow", "Exit"))
        self.actionImport_images.setText(_translate("MainWindow", "Import imagery"))
        # self.actionHow_to_use.setText(_translate("MainWindow", "How to use？"))
        self.actionSave_and_exit.setText(_translate("MainWindow", "Save and exit"))
        self.actionExit_directly.setText(_translate("MainWindow", "Exit directly"))

    def Import_Imagery(self):
        try:
            qfile = QtWidgets.QFileDialog.getOpenFileName(None, "Import Imagery", ".",
                                                          "Image files (*.bmp *.jpg *.png *.jpeg)")
            self.original_img = cv_imread(qfile[0])
            y, x = self.original_img.shape[:-1]  # 获取图片大小
            ratio = float(y / x)
            new_y = 320
            # new_x = int(320 / ratio)
            new_x = int(new_y / ratio)
            cvimg = cv2.resize(self.original_img, (new_x, new_y))
            cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)  # BGR转RGB
            frame = QtGui.QImage(cvimg.data, new_x, new_y, new_x * 3, QtGui.QImage.Format_RGB888)  # 转为QImage格式
            self.scene_original.clear()  # 清空画布
            pix = QtGui.QPixmap.fromImage(frame)
            self.scene_original.addPixmap(pix)
        except:
            self.scene_original.clear()

    def start(self):
        function = self.comboBox_function.currentText()
        partitions_R = self.spinBox_R.value()
        partitions_G = self.spinBox_G.value()
        partitions_B = self.spinBox_B.value()
        parameters = {"Evaluation": function, "Red channel class_no": partitions_R,
                      "Green channel class_no": partitions_G, "Blue channel class_no": partitions_B}
        try:
            self.scene_segmented.clear()  # 清空画布
            self.scene_R.clear()
            self.scene_G.clear()
            self.scene_B.clear()
            self.progressBar.setProperty("value", 0)  # 重置进度条

            # 清空表格
            self.tableWidget.clearContents()

            for i in range(1, 21):
                time.sleep(0.01)
                self.progressBar.setProperty("value", i)

            to_be_seg = BaseFunctions.Segment(**parameters)
            self.RGB_thresholds, RGB_segres = to_be_seg.segment(BaseFunctions.Image(self.original_img).BGR2RGB)
            self.segmented_img = cv2.merge([RGB_segres[2].astype(np.uint8), RGB_segres[1].astype(np.uint8),
                                            RGB_segres[0].astype(np.uint8)])  # 还原BGR并将类型转换为opencv可支持的uint8
            zeros = np.zeros(RGB_segres[0].shape, dtype="uint8")
            self.segmented_R = cv2.merge([zeros, zeros, RGB_segres[0].astype(np.uint8)])
            self.segmented_G = cv2.merge([zeros, RGB_segres[1].astype(np.uint8), zeros])
            self.segmented_B = cv2.merge([RGB_segres[2].astype(np.uint8), zeros, zeros])  # 三通道矩阵
            for i in range(21, 41):
                time.sleep(0.01)
                self.progressBar.setProperty("value", i)

            y_segmented, x_segmented = self.segmented_img.shape[:-1]  # 获取图片大小
            ratio = float(y_segmented / x_segmented)
            new_y_segmented = 330  # 大窗口高度
            new_x_segmented = int(330 / ratio)
            cvimg_segmented = cv2.resize(self.segmented_img, (new_x_segmented, new_y_segmented))  # 重新缩放大小
            cvimg_segmented = cv2.cvtColor(cvimg_segmented, cv2.COLOR_BGR2RGB)  # BGR转RGB
            frame_segmented = QtGui.QImage(cvimg_segmented.data, new_x_segmented, new_y_segmented, new_x_segmented * 3,
                                           QtGui.QImage.Format_RGB888)  # 转为QImage格式
            pix_segmented = QtGui.QPixmap.fromImage(frame_segmented)
            self.scene_segmented.addPixmap(pix_segmented)
            for i in range(41, 61):
                time.sleep(0.01)
                self.progressBar.setProperty("value", i)

            new_y_sep = 100  # 小窗口高度
            new_x_sep = int(100 / ratio)

            cvimg_sep_R = cv2.resize(self.segmented_R, (new_x_sep, new_y_sep))  # 重新缩放大小
            cvimg_sep_R = cv2.cvtColor(cvimg_sep_R, cv2.COLOR_BGR2RGB)
            frame_sep_R = QtGui.QImage(cvimg_sep_R.data, new_x_sep, new_y_sep, new_x_sep * 3,
                                       QtGui.QImage.Format_RGB888)  # 转为QImage格式
            pix_sep_R = QtGui.QPixmap.fromImage(frame_sep_R)
            self.scene_R.addPixmap(pix_sep_R)

            cvimg_sep_G = cv2.resize(self.segmented_G, (new_x_sep, new_y_sep))  # 重新缩放大小
            cvimg_sep_G = cv2.cvtColor(cvimg_sep_G, cv2.COLOR_BGR2RGB)
            frame_sep_G = QtGui.QImage(cvimg_sep_G.data, new_x_sep, new_y_sep, new_x_sep * 3,
                                       QtGui.QImage.Format_RGB888)  # 转为QImage格式
            pix_sep_G = QtGui.QPixmap.fromImage(frame_sep_G)
            self.scene_G.addPixmap(pix_sep_G)

            cvimg_sep_B = cv2.resize(self.segmented_B, (new_x_sep, new_y_sep))  # 重新缩放大小
            cvimg_sep_B = cv2.cvtColor(cvimg_sep_B, cv2.COLOR_BGR2RGB)
            frame_sep_B = QtGui.QImage(cvimg_sep_B.data, new_x_sep, new_y_sep, new_x_sep * 3,
                                       QtGui.QImage.Format_RGB888)  # 转为QImage格式
            pix_sep_B = QtGui.QPixmap.fromImage(frame_sep_B)
            self.scene_B.addPixmap(pix_sep_B)
            for i in range(61, 81):
                time.sleep(0.01)
                self.progressBar.setProperty("value", i)

            if max([partitions_R, partitions_G, partitions_B]) - 1 > 10:  # 判断最大阈值个数
                newcol = max([partitions_R, partitions_G, partitions_B]) - 1
                self.tableWidget.setColumnCount(newcol)  # 设置列数

            for i in range(3):  # 阈值显示
                for j in range(len(self.RGB_thresholds[i])):
                    newitem = QtWidgets.QTableWidgetItem(str(round(self.RGB_thresholds[i][j])))  # 最优阈值取整
                    newitem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)  # 单元格水平和竖直对齐
                    self.tableWidget.setItem(i, j, newitem)
            for i in range(81, 100):
                time.sleep(0.01)
                self.progressBar.setProperty("value", i)

            self.progressBar.setProperty("value", 100)

        except AttributeError:  # 判断是否已导入图片
            msb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'Error', 'Import an image first!')
            msb.setWindowIcon(QtGui.QIcon(":\icon.ico"))
            msb.exec_()
            self.progressBar.setProperty("value", 0)

    def save_as_file(self):
        try:
            saveFilePath = QtWidgets.QFileDialog.getSaveFileName(None, "Save as file", "Segmented Imagery.jpeg",
                                                                 filter="jpeg (*.jpeg);;jpg (*.jpg);;png (*.png)")
            cv_imwrite(self.segmented_img, saveFilePath[0])
        except AttributeError:  # 判断是否已分割图片
            msb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'Error', 'Start segmentation first!')
            msb.setWindowIcon(QtGui.QIcon(":\icon.ico"))
            msb.exec_()
        except Exception:
            pass

    def save_R_image(self):
        try:
            saveFilePath = QtWidgets.QFileDialog.getSaveFileName(None, "Save R image", "R image.jpeg",
                                                                 filter="jpeg (*.jpeg);;jpg (*.jpg);;png (*.png)")
            cv_imwrite(self.segmented_R, saveFilePath[0])
        except AttributeError:
            msb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'Error', 'Start segmentation first!')
            msb.setWindowIcon(QtGui.QIcon(":\icon.ico"))
            msb.exec_()
        except Exception:
            pass

    def save_G_image(self):
        try:
            saveFilePath = QtWidgets.QFileDialog.getSaveFileName(None, "Save G image", "G image.jpeg",
                                                                 filter="jpeg (*.jpeg);;jpg (*.jpg);;png (*.png)")
            cv_imwrite(self.segmented_G, saveFilePath[0])
        except AttributeError:
            msb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'Error', 'Start segmentation first!')
            msb.setWindowIcon(QtGui.QIcon(":\icon.ico"))
            msb.exec_()
        except Exception:
            pass

    def save_B_image(self):
        try:
            saveFilePath = QtWidgets.QFileDialog.getSaveFileName(None, "Save B image", "B image.jpeg",
                                                                 filter="jpeg (*.jpeg);;jpg (*.jpg);;png (*.png)")
            cv_imwrite(self.segmented_B, saveFilePath[0])
        except AttributeError:
            msb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'Error', 'Start segmentation first!')
            msb.setWindowIcon(QtGui.QIcon(":\icon.ico"))
            msb.exec_()
        except Exception:
            pass

    def export_result_as_file(self):
        try:
            saveFilePath = QtWidgets.QFileDialog.getSaveFileName(None, "Export result as file", "RGB_Thresholds.xlsx",
                                                                 filter="xlsx (*.xlsx);;xls (*.xls);;csv (*.csv)")
            f = xlwt.Workbook()  # 创建工作簿
            sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=True)
            title = ['R Channel', 'G Channel', 'B Channel']  # 每行表头
            for i in range(3):
                for j in range(len(self.RGB_thresholds[i])):
                    sheet1.write(i, 0, title[i])
                    sheet1.write(i, j + 1, round(float(self.RGB_thresholds[i][j]), 3))
            sheet1.col(0).width = 256 * 12  # 设置首列列宽
            f.save(saveFilePath[0])
        except AttributeError:
            msb = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, 'Error', 'Start segmentation first!')
            msb.setWindowIcon(QtGui.QIcon(":\icon.ico"))
            msb.exec_()
        except Exception:
            pass

    def save_and_exit(self):
        try:
            path = os.getcwd() + "\\" + "temp_" + str(time.time()).replace(".", "_")
            os.mkdir(path)

            cv_imwrite(self.segmented_img, os.path.join(path, "segmented image.png"))
            cv_imwrite(self.segmented_R, os.path.join(path, "R image.png"))
            cv_imwrite(self.segmented_G, os.path.join(path, "G image.png"))
            cv_imwrite(self.segmented_B, os.path.join(path, "B image.png"))

            f = xlwt.Workbook()  # 创建工作簿
            sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=True)
            title = ['R Channel', 'G Channel', 'B Channel']  # 每行表头
            for i in range(3):
                for j in range(len(self.RGB_thresholds[i])):
                    sheet1.write(i, 0, title[i])
                    sheet1.write(i, j + 1, round(float(self.RGB_thresholds[i][j]), 3))
            sheet1.col(0).width = 256 * 12  # 设置首列列宽
            f.save(path + r"\RGB_thresholds.xlsx")
            self.exit()
        except:
            self.exit()

    def exit(self):
        sys.exit(0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # 创建一个QApplication
    MainWindow = QtWidgets.QMainWindow()  # 创建一个QMainWindow
    ui = Ui_MainWindow()  # Ui_MainWindow()类的实例化对象
    ui.setupUi(MainWindow)  # 执行setupUi方法
    MainWindow.show()  # 显示QMainWindow
    sys.exit(app.exec_())
