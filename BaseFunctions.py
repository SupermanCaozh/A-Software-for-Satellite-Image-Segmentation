import numpy as np
import matplotlib.pyplot as plt
import numba as nb
import pandas as pd
import cv2
import random

from image_similarity_measures import quality_metrics


# 交互过程只用实例Image和Segment

class Image:
    def __init__(self, img):
        """
        存储被读取的图片文件,并保留其各种属性
        :param img: cv2图像实例
        """
        self._img = img

        # 存储图像的大小,包括行列数
        self._nrow = self._img.shape[0]
        self._ncol = self._img.shape[1]
        self._total_pixel = self._nrow * self._ncol

        self.b, self.g, self.r = cv2.split(self._img)
        # self.b_hist = (cv2.calcHist([self.b], [0], None, [256], [0, 256]))[:, 0]
        # self.g_hist = (cv2.calcHist([self.g], [0], None, [256], [0, 256]))[:, 0]
        # self.r_hist = (cv2.calcHist([self.r], [0], None, [256], [0, 256]))[:, 0]

    @property
    def BGR2RGB(self):
        # 由于cv2读取的图像为BGR模式,转变成RGB模式并返回[R,G,B]三维矩阵
        return np.array([self.r, self.g, self.b])  # (3*height*width)

    @property
    def TotalPixel(self):
        # 返回图像总像素个数属性
        return self._total_pixel


class Optimizer:
    """
    优化器Base类,用以寻找最优阈值
    参数可以设定好（除阈值个数）

    注：该类中的属性和方法都可以在Segment类中直接调用
    """

    def __init__(self, **kwargs):
        # 优化终止条件
        self._MaxIter = 150

        # 优化目标
        self._objf = kwargs["Evaluation"]  # str字符串
        # 原文中使用的种群规模为50，此处为提高效率使用30，经测试同样可以满足精度要求
        self._popnum = 30
        self._betanum = 2
        self._deltanum = 3

    def otsu(self, solution, hist, totp):
        """
        计算""Otsu's between-class variance""目标函数值(对应GUI中用户选择使用的”Otsu's between-class variance")
        :param solution: 用于计算目标函数的解——(1,n)维numpy.ndarray类型（建议）或list类
        :param hist: 依赖图像的灰度直方图进行分割
        :param totp: 图像中的像素总个数
        :return: sum(var) 返回计算得到的目标值,在optimize方法中被引用
        """
        var = []
        solution_exp = np.append(np.append(0, solution), 255)
        ints = np.arange(256)
        p = hist / totp
        mean_g = np.dot(ints, p)
        for i in range(len(solution_exp) - 1):
            t1 = int(solution_exp[i])
            t2 = int(solution_exp[i + 1])
            if solution_exp[i + 1] == 256:
                w = np.sum(p[t1:256])
            else:
                w = np.sum(p[t1:t2])
            if w != 0:
                if solution_exp[i + 1] == 255:
                    miu = np.dot(ints[t1:256], p[t1:256]) / w
                else:
                    miu = np.dot(ints[t1:t2], p[t1:t2]) / w
                var.append(w * ((miu - mean_g) ** 2))
        return np.sum(var)

    def kapur(self, solution, hist, totp):
        """
        计算"Kapur's Entropy"目标函数值(对应GUI中用户选择使用的"Kapur's Entropy")
        :param solution: 用于计算目标函数的解
        :param hist: 依赖图像的灰度直方图进行分割
        :return: sum(etrp) 返回计算得到的目标值,在optimize方法中被引用
        """
        etrp = []
        solution_exp = np.append(np.append(0, solution), 255)
        ints = np.arange(256)
        p = hist / totp
        for i in range(len(solution_exp) - 1):
            t1 = int(solution_exp[i])
            t2 = int(solution_exp[i + 1])
            if solution_exp[i + 1] == 256:
                w = np.sum(p[t1:256])
            else:
                w = np.sum(p[t1:t2])
            if w != 0:
                if solution_exp[i + 1] == 255:
                    k1 = p[t1:256] / w
                else:
                    k1 = p[t1:t2] / w
                k2 = np.log(k1)
                k = -1 * np.dot(k1, k2)
                etrp.append(k)
        return np.sum(etrp)

    def tsallis(self, solution, hist, totp):
        """
        计算"Tsallis's Entropy"目标函数值(对应GUI中用户选择使用的"Tsallis's Entropy")
        :param solution: 用于计算目标函数的解
        :return:  返回计算得到的目标值,在optimize方法中被引用
        """
        tsas = []
        solution_exp = np.append(np.append(0, solution), 255)
        ints = np.arange(256)
        p = hist / totp
        for i in range(len(solution_exp) - 1):
            t1 = int(solution_exp[i])
            t2 = int(solution_exp[i + 1])
            if solution_exp[i + 1] == 256:
                P = np.sum(p[t1:256])
            else:
                P = np.sum(p[t1:t2])
            if P != 0:
                if solution_exp[i + 1] == 255:
                    temp = (p[t1:256] / P) ** 4
                    # q=4 较为适合卫星图像分割
                else:
                    temp = (p[t1:t2] / P) ** 4
                S = (1 - np.sum(temp)) / (4 - 1)
                tsas.append(S)
        return np.sum(tsas) + (1 - 4) * np.multiply.reduce(np.array(tsas))

    def fitness(self, solution, hist, totp):
        """
        根据用户选择的目标函数,确定算法优化过程中使用的目标函数
        :param solution: 用于计算目标函数的解
        :return: 根据self._objf确定返回的目标函数值
        """
        if self._objf == "Otsu's between-class variance":
            return self.otsu(solution, hist, totp)
        elif self._objf == "Kapur's Entropy":
            return self.kapur(solution, hist, totp)
        else:
            return self.tsallis(solution, hist, totp)

    def optimize(self, no_class, hist, totp):
        """
        返回单通道最优阈值
        :return:thresholds：最优的阈值,在segmentbase方法中被引用
        """
        random.seed(516)
        Alpha_pos = np.zeros(no_class)
        Alpha_score = float("-inf")
        Beta_pos = np.zeros((2, no_class))
        Beta_score = np.array([float("-inf") for i in range(self._betanum)])
        Delta_pos = np.zeros((3, no_class))
        Delta_score = np.array([float("-inf") for i in range(self._deltanum)])
        Positions = 0 + np.random.uniform(0, 1, (self._popnum, no_class)) * (255 - 0)
        Positions = np.sort(Positions, axis=1)

        for t in range(self._MaxIter):
            for i in range(self._popnum):
                fit = self.fitness(np.floor(Positions[i, :]), hist, totp)
                if fit > Alpha_score:
                    Alpha_score = fit
                    Alpha_pos = Positions[i, :]
                else:
                    flag = 0
                    for j in range(self._betanum):
                        if fit > Beta_score[j]:
                            Beta_score[j] = fit
                            Beta_pos[j] = Positions[i, :]
                            flag = 1
                            break
                        else:
                            continue
                    # 若beta种群未更新
                    if flag == 0:
                        for j in range(self._deltanum):
                            if fit > Delta_score[j]:
                                Delta_score[j] = fit
                                Delta_pos[j] = Positions[i, :]
                                break
                            else:
                                continue
            std = 1 - (t / self._MaxIter)
            wa = 0.5
            wb = 0.3
            wd = 0.2

            betapos = np.mean(Beta_pos, axis=0)
            deltapos = np.mean(Delta_pos, axis=0)
            error = np.random.randn(no_class) * std
            Prey_pos = wa * Alpha_pos + wb * betapos + wd * deltapos + error
            for i in range(self._popnum):
                r = np.random.uniform(-2, 2, no_class)
                new_pos = Prey_pos - r * abs(Prey_pos - Positions[i, :])

                idxu = np.where(new_pos > 255)
                idxl = np.where(new_pos < 0)
                if idxu[0].size > 0:
                    u = np.random.uniform(0, 1, len(idxu[0]))
                    new_pos[idxu] = Positions[i, idxu] + u * (255 - Positions[i, idxu])
                if idxl[0].size > 0:
                    u = np.random.uniform(0, 1, len(idxl[0]))
                    new_pos[idxl] = Positions[i, idxl] + u * (0 - Positions[i, idxl])

                Positions[i, :] = np.sort(new_pos)
        return np.round(Alpha_pos)


class Segment(Optimizer):
    # 继承Optimizer,覆盖Optimizer的方法
    def __init__(self, **kwargs):
        """
        Segmentation Process
        :param kwargs: 不定参数,包括Red/Green/Blue channel class_no,对应GUI界面中用户通过数字滚条选择的分割出几个类别
        """
        super(Segment, self).__init__(**kwargs)
        # self._Algorithm = Alogrithm
        # self._Objf = Objf

        # 类别个数=阈值个数+1
        self.no_class = [kwargs["Red channel class_no"] - 1,  # float或int数字
                         kwargs["Green channel class_no"] - 1,
                         kwargs["Blue channel class_no"] - 1]

        self.output = [None for i in range(3)]  # 存储分割后结果

    def segmentbase(self, img2d, no_class):
        """
        分割单通道(单层,即仅二维矩阵)灰度图
        :param img2d: 二维矩阵图像,存储像素灰度——建议使用numpy.ndarray类型
        :return:[thresholds,segmented_img]:[最优的阈值,分割所得图像]
        """
        hist = (cv2.calcHist([img2d], [0], None, [256], [0, 256]))[:, 0]
        totp = np.sum(hist)
        thresholds = self.optimize(no_class, hist, totp)

        # 依据thresholds分割图像
        t_exp = np.append(np.append(0, thresholds), 255)
        output = np.ones(img2d.shape) * 255
        for i in range(len(t_exp) - 1):
            idx = np.where((img2d >= t_exp[i]) & (img2d < t_exp[i + 1]))
            output[idx] = t_exp[i]
        return [thresholds, output]

    def segment(self, img3d):
        """
        分割用户导入图像,RGB mode/Grayscale
        :param img3d:[[R],[G],[B]]三通道数组,shape=(3,nrow,ncol)——建议使用numpy.ndarray类型
        :return:rgb_thresholds:存储R,G,B三通道最优阈值
        :return:rgb_segres：存储R,G,B三通道分割所得图像,shape=(3,nrow,ncol)
        """
        R_res = self.segmentbase(img3d[0], self.no_class[0])
        G_res = self.segmentbase(img3d[1], self.no_class[1])
        B_res = self.segmentbase(img3d[2], self.no_class[2])
        rgb_thresholds = [R_res[0], G_res[0], B_res[0]]
        rgb_segres = np.array([R_res[1], G_res[1], B_res[1]])
        return rgb_thresholds, rgb_segres

    # IQA Metrics
    # def psnr(self):
    #     pass
    #
    # def mse(self):
    #     pass
    #
    # def fsim(self):
    #     pass
    #
    # def ssim(self):
    #     pass
