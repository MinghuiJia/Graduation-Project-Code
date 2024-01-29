# -*- coding: utf-8 -*-
# 读取符合要求的筛选数据，并拟合和可视化，完成角度归一化(使用梯度下降)

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
import matplotlib.ticker as ticker
import math
import scipy.stats as stats
from matplotlib import font_manager
import datetime as dtime
import matplotlib as mat

import scipy.optimize

# 读取并解析文件
def readFile(filePath):
    f = open(filePath,'r')
    lines = f.readlines()
    pointNumLngLatMap = {}
    pointsDic = {}
    for i in range(len(lines)):
        if (i == 0):
            pass
        # 解析数据
        else:
            temp_list = lines[i].split(":")
            pointNum = temp_list[0]
            pointLngLat = temp_list[1]
            pointsDic[pointNum] = []
            pointNumLngLatMap[pointNum] = pointLngLat
            info_list = temp_list[2].split(";")
            for k in range(len(info_list)):
                value_list = info_list[k].split(",")
                # [NTLValue, Zenith, YYYYMMDD]
                pointsDic[pointNum].append([float(value_list[2]),float(value_list[1]),value_list[0]])

    new_pointsDic = {}
    new_pointNumLngLatMap = {}
    for key in pointsDic:
        if (len(pointsDic[key]) < 10):
            continue
        new_pointsDic[key] = pointsDic[key]
        new_pointNumLngLatMap[key] = pointNumLngLatMap[key]
    return new_pointNumLngLatMap,new_pointsDic

# 计算决定系数R2
def calGoodnessOfFit(y,y_true):
    y_true_mean = np.mean(y_true)
    sstotal = 0
    ssres = 0
    for i in range(len(y)):
        sstotal += math.pow(y_true[i]-y_true_mean,2)
        ssres += math.pow(y_true[i]-y[i],2)
    score = 1-(ssres/sstotal)
    return score

# 计算两个变量的相关系数
def calCorrelation(x_array,y_array):
    # 计算相关系数
    ave_x = np.mean(np.array(x_array))
    ave_y = np.mean(np.array(y_array))
    # 离差
    dev_x = np.array(x_array) - ave_x
    dev_y = np.array(y_array) - ave_y
    # 协方差
    cov_xy = np.mean(dev_x * dev_y)
    std_x = np.std(np.array(x_array))
    std_y = np.std(np.array(y_array))
    if (std_x == 0 or std_y == 0):
        return "nan"
    correlation = cov_xy / (np.std(np.array(x_array)) * np.std(np.array(y_array)))
    return correlation

# 需要拟合的函数func
def func(p, x):
    a, b, c = p
    return a * x ** 2 + b * x + c

def func1(p, x):
    a, b = p
    return a * x ** 2 + b * x + 1

# 偏差函数：x,y都是列表:这里的x,y和上面的Xi,Yi中是一一对应的
def error(p, x, y):
    return (1/len(x))*(func(p, x) - y)**2

def error1(p, x, y):
    y_mean = np.mean(y)
    x_mean = np.mean(func1(p,x))
    # return ((func1(p, x) - y)**2) / ((y - y_mean)**2)
    return (1 / len(x)) * (func1(p, x) - y) ** 2
    # return a / (func1(p, x) - x_mean)*(y - y_mean)

# 角度归一化，并展示变化前后散点图
def normalizationZenith(visX_dic,visY_dic,outputFile,output_params_path):
    f = open(outputFile, 'w')
    f1 = open(output_params_path, 'w')

    normalizationResult_array = []
    for key in visX_dic:
        # 计算相关系数
        # 二次拟合(多项式拟合)
        parameters = np.polyfit(visX_dic[key], visY_dic[key], 2)
        # 用于绘图
        x = np.arange(0, 90, 0.02)
        y = parameters[0] * x ** 2 + parameters[1] * x ** 1 + parameters[2]
        # 求解 a,b,c系数（最小二乘拟合）
        parameter_init = np.array([0, 0, 0])
        # 把error函数中除了p0以外的参数打包到args中(使用要求)
        Para = leastsq(error, parameter_init, args=(np.array(visX_dic[key]), np.array(visY_dic[key])))
        # 读取结果
        a, b, c = Para[0]
        print("use leastsq: ", "a=", a, "b=", b, "c=", c)
        print("use polyfit: ", "a=", parameters[0], "b=", parameters[1], "c=", parameters[2])
        # 用于绘图
        x_leastsq = np.arange(0, 90, 0.02)
        y_leastsq = a * x ** 2 + b * x ** 1 + c

        # 求解a,b系数
        parameter_init1 = np.array([0, 0])
        # 把error函数中除了p0以外的参数打包到args中(使用要求)
        Para1 = leastsq(error1, parameter_init1,
                        args=(np.array(visX_dic[key]), np.array(visY_dic[key]) / parameters[2]))
        # 读取结果
        a1, b1 = Para1[0]
        print("use leastsq: ", "a1=", a1, "b1=", b1)

        # 计算拟合的R2
        fit_y = parameters[0] * np.array(visX_dic[key]) ** 2 + parameters[1] * np.array(visX_dic[key]) ** 1 + \
                parameters[2]
        GoodnessOfFit_score = calGoodnessOfFit(fit_y, np.array(visY_dic[key]))
        r, p = stats.pearsonr(fit_y, np.array(visY_dic[key]))
        print("goodness of quadratic fit polyfit(R2):", GoodnessOfFit_score)
        print("person r2:", math.pow(r, 2), " p value:", p)
        # 计算最小二乘拟合的R2
        fit_y_leastsq = a * np.array(visX_dic[key]) ** 2 + b * np.array(visX_dic[key]) ** 1 + c
        GoodnessOfFit_score_leastsq = calGoodnessOfFit(fit_y_leastsq, np.array(visY_dic[key]))
        print("goodness of quadratic fit leastsq(R2):", GoodnessOfFit_score_leastsq)

        ## new
        Z = np.array(visX_dic[key])
        R = np.array(visY_dic[key])
        T = [float(i) for i in range(1,len(visX_dic[key])+1)]
        T = np.array(T)

        # ## R = c(t) + az2 + bz  => c(t) = ct + d
        # banana = lambda p: np.sum(np.power(
        #     R -
        #     (p[0] * (np.power(Z, 2)) + p[1] * Z) -
        #     (p[2] * T + np.array([p[3]] * len(Z)))
        #     , 2))
        # p0 = np.array([parameters[0], parameters[1], 0, parameters[2]])
        # # p0 = np.array([1, 1, 1, 10])

        ## R = c(t) * (az2 + bz + 1)  => c(t) = ct + d
        # banana = lambda p: np.sum(np.power(
        #     R -
        #     (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))) *
        #     (p[2] * T + np.array([p[3]] * len(Z)))
        #     , 2))


        # (R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))))
        # (p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z)))
        # (len(Z) * np.sum(((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z)))) * (p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z))))) -
        # np.sum((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))))) * np.sum((p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z))))) /
        # (math.sqrt(len(Z) * np.sum((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z)))) * (R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))))) - np.power(np.sum((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))))),2)) *
        # math.sqrt(len(Z) * np.sum((p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z))) * (p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z)))) - np.power(np.sum((p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z)))),2)))

        # p = np.array([parameters[0] / parameters[2], parameters[1] / parameters[2], 0.001, 0.001, parameters[2]])
        # aaaa = (len(Z) * np.sum(((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z)))) * (
        #             p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z))))) - np.sum(
        #     (R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))))) * np.sum(
        #     (p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z)))))
        #
        # print(aaaa)
        # bbbb = math.sqrt(len(Z) * np.sum(np.power((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z)))),2)) - np.power(np.sum((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))))),2))
        # print(bbbb)
        # cccc = math.sqrt(len(Z) * np.sum(np.power((p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z))),2)) - np.power(np.sum((p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z)))),2))
        # print(cccc)
        p_final = 0
        p0 = np.array([parameters[0] / parameters[2], parameters[1] / parameters[2], 0, 0, parameters[2]])
        for it in range(1):
            banana = lambda p: np.power((len(Z) * np.sum(((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z)))) * (
                        p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z))))) - np.sum(
                (R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))))) * np.sum(
                (p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z))))) / (np.sqrt(len(Z) * np.sum(np.power((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z)))),2)) - np.power(np.sum((R / (p[0] * (np.power(Z, 2)) + p[1] * Z + np.array([1] * len(Z))))),2)) * np.sqrt(len(Z) * np.sum(np.power((p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z))),2)) - np.power(np.sum((p[2] * (np.power(Z, 2)) + p[3] * Z + np.array([p[4]] * len(Z)))),2))),2)

            p_final = scipy.optimize.fmin(func=banana, x0=p0)

            # 修正系数
            normalizationY = R / (p_final[0] * (np.power(Z, 2)) + p_final[1] * Z + np.array([1] * len(Z)))
            parameters1 = np.polyfit(Z, normalizationY, 2)

            p0 = np.array([p_final[0], p_final[1], p_final[2], p_final[3], parameters1[2]])
            print(p_final)

        # normalizationY = R - (p_final[0] * (np.power(Z, 2)) + p_final[1] * Z) #+ np.array([25] * len(Z))
        normalizationY = R / (p_final[0] * (np.power(Z, 2)) + p_final[1] * Z + np.array([1] * len(Z)))

        res = np.where(normalizationY < 0)
        for re in res:
            normalizationY[re] = R[re]


        normalizationResult_array.append(normalizationY)


        f.write(key + ":" + str(math.pow(r, 2)) + "\n")
        f1.write(key + ":" + str(p_final[0]) + "," + str(p_final[1]) + "," + str(p_final[2]) + "," + str(p_final[3]) + "\n")

        # ## 需要后期注释掉的
        # # 计算拟合的R2
        # fit_y = parameters[0] * np.array(visX_dic[key]) ** 2 + parameters[1] * np.array(visX_dic[key]) ** 1 + parameters[2]
        # GoodnessOfFit_score = calGoodnessOfFit(fit_y, np.array(visY_dic[key]))
        # r, p = stats.pearsonr(fit_y, np.array(visY_dic[key]))
        # print("goodness of quadratic fit polyfit(R2):",GoodnessOfFit_score)
        # print("person r2:", math.pow(r,2)," p value:",p)
        # # 计算最小二乘拟合的R2
        # fit_y_leastsq = a * np.array(visX_dic[key]) ** 2 + b * np.array(visX_dic[key]) ** 1 + c
        # GoodnessOfFit_score_leastsq = calGoodnessOfFit(fit_y_leastsq, np.array(visY_dic[key]))
        # print("goodness of quadratic fit leastsq(R2):", GoodnessOfFit_score_leastsq)
        #
        # r1, p1 = stats.pearsonr(normalizationY, np.array(visY_dic[key]))
        # print("person 1 r2:", math.pow(r1,2)," p value:",p1)
        #
        # f.write(key + "polyfit quadratic R2:" + str(GoodnessOfFit_score) + ",point num:" + str(len(visX_dic[key])) +
        #         ",a:" + str(parameters[0]) + ",b:" + str(parameters[1]) + ",c:" + str(parameters[2]) + "\n")
        # f.write(key + "person R2:" + str(math.pow(r,2)) + ",p value:" + str(p) + "\n")
        # f.write(key + "leastsq quadratic R2:" + str(GoodnessOfFit_score_leastsq) + ",point num:" + str(len(visX_dic[key])) +
        #         ",a:" + str(a) + ",b:" + str(b) + ",c:" + str(c) + "\n")
        # f.write(key + "leastsq solve:" + ",a1:" + str(a1) + ",b1:" + str(b1) + ",c1:" + str(1) + "\n")
        # f.write(key + ":" + str(math.pow(r,2)) + "\n")
        #
        # # 二次拟合(多项式拟合)
        # parameters = np.polyfit(visX_dic[key], visY_dic[key], 2)
        # # 用于绘图
        # x = np.arange(0, 90, 0.02)
        # y = parameters[0] * x ** 2 + parameters[1] * x ** 1 + parameters[2]
        #
        # # plt.tick_params
        # plt.figure(figsize=(8, 6))
        # plt.rcParams['font.sans-serif'] = ['SimHei','Adobe Gothic Std']
        # # plt.tick_params(labelsize=16)
        #
        # # 可视化散点和拟合曲线
        # plt.scatter(visX_dic[key], visY_dic[key], color='black', s=5, label='original points')
        # # plt.scatter(visX_dic[key], visY_dic[key], color='black', s=5, label='原始观测数据')
        # ccc = np.array(normalizationY) * 1
        # plt.scatter(visX_dic[key], ccc, color='green', s=10, label='correct points')
        # # plt.plot(x, y, color='red', label='quadratic fit')
        # plt.plot(x, y, color='red', label='二次拟合曲线')
        # # plt.title(r"$\bf{Los\ Angeles\ " + key + "}$",{'size': 16})   #Phoenix    #Las Vegas Kathmandu Las\ Vegas\
        # # plt.title(r"北干巴鲁2号研究点", fontproperties="SimHei",fontsize=22)  # Phoenix    #Las Vegas Kathmandu Las\ Vegas\
        #
        # # plt.xlabel(r"$\bf{VZA(Degree)}$",{'size': 16})
        # plt.xlabel(u"传感器观测天顶角（度）", fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf",weight='extra bold'),fontsize=22)
        # # plt.ylabel(r"$\bf{DNB\ BRDF-Corrected\ NTL\ Radiance}$",{'size': 16})
        # plt.ylabel(r"每日月光与大气校正后的夜间灯光辐射值", labelpad=5,fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf",weight='extra bold'),fontsize=22)
        # plt.legend(loc="upper right",prop={'size': 22,"family" : "SimHei"})
        # plt.yticks(fontproperties=font_manager.FontProperties(
        #     fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        # plt.xticks(fontproperties=font_manager.FontProperties(
        #     fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        # plt.tick_params(labelsize=20)
        # plt.show()
    f1.close()
    f.close()
    return normalizationResult_array

# 可视化角度和夜光值之间的关系，拟合并归一化，将归一化后的数据保存在文件中
def visScatterAndFitCurve(result_dic,outputFile,fit_result_path,pointNumLngLatMap,output_params_path):
    f1 = open(fit_result_path,'w')
    # 创建文件，并写入表头信息
    # content_str = ""
    # point_count = 0
    # for key in pointNumLngLatMap:
    #     if (point_count == 0):
    #         content_str += key+":"+str(pointNumLngLatMap[key][0])+","+str(pointNumLngLatMap[key][1])
    #     else:
    #         content_str += ";"+key+":"+str(pointNumLngLatMap[key][0])+","+str(pointNumLngLatMap[key][1])
    #     point_count += 1
    # f1.write(content_str + "\n")
    f1.write("pointNum:lng,lat(left top):YYYYMMDD,Zenith,NTLValue;..." + "\n")

    # 数据组织
    visX_dic = {}
    visY_dic = {}
    visTime_dic = {}
    for key in result_dic:
        x_value = []
        y_value = []
        time_value = []
        for i in range(len(result_dic[key])):
            y_value.append(result_dic[key][i][0])
            x_value.append(result_dic[key][i][1])
            time_value.append(int(result_dic[key][i][2]))
        visX_dic[key] = x_value
        visY_dic[key] = y_value
        visTime_dic[key] = time_value

    print(visX_dic)
    print(visY_dic)
    print(visTime_dic)

    # 角度校正
    normalizationResult_array = normalizationZenith(visX_dic,visY_dic,outputFile, output_params_path)

    # 校正数据写入文件
    norm_index = 0
    for key in visX_dic:
        f1.write(key + ":" + pointNumLngLatMap[key] + ":")
        for k in range(len(normalizationResult_array[norm_index])):
            if (k == 0):
                f1.write(str(visTime_dic[key][k]) + "," + str(visX_dic[key][k]) + "," + str(normalizationResult_array[norm_index][k]))
            else:
                f1.write(
                    ";" + str(visTime_dic[key][k]) + "," + str(visX_dic[key][k]) + "," + str(normalizationResult_array[norm_index][k]))
        f1.write("\n")
        norm_index += 1

    f1.close()

# 可视化时间序列，并计算NDHDNTL
def visTimeSeries(pointsDic,pointsDic_fit, area):
    # 处理未校正数据
    pointsDic_less10 = {}
    for key in pointsDic:
        pointsDic_less10[key] = []
        for item in pointsDic[key]:
            # if (50 < item[1] < 60):
            # if (45 < item[1] < 50):
            # if (40 < item[1] < 45):
            # if (30 < item[1] < 40):
            # if (20 < item[1] < 30):
            # if (10 < item[1] < 20):
            # if (item[1] < 10):
            if (item[1]):
                item_temp = [item[0],item[1],int(item[2])]
                pointsDic_less10[key].append(item_temp)
        pointsDic_less10[key].sort(key = lambda x:x[2]) #指定某列排序

    visNTL_dic = {}
    visTime_dic = {}
    for key in pointsDic_less10:
        NTL_value = []
        time_value = []
        for i in range(len(pointsDic_less10[key])):
            NTL_value.append(pointsDic_less10[key][i][0])
            time_value.append(str(pointsDic_less10[key][i][2]))
        visNTL_dic[key] = NTL_value
        visTime_dic[key] = time_value

    # 处理校正数据
    pointsDic_less10_fit = {}
    for key in pointsDic_fit:
        pointsDic_less10_fit[key] = []
        for item in pointsDic_fit[key]:
            if str(item[2]) in visTime_dic[key]:
                item_temp = [item[0], item[1], int(item[2])]
                pointsDic_less10_fit[key].append(item_temp)
        pointsDic_less10_fit[key].sort(key=lambda x: x[2])  # 指定某列排序

    visNTL_dic_fit = {}
    visTime_dic_fit = {}
    for key in pointsDic_less10_fit:
        NTL_value_fit = []
        time_value_fit = []
        for i in range(len(pointsDic_less10_fit[key])):
            NTL_value_fit.append(pointsDic_less10_fit[key][i][0])
            time_value_fit.append(str(pointsDic_less10_fit[key][i][2]))
        visNTL_dic_fit[key] = NTL_value_fit
        visTime_dic_fit[key] = time_value_fit

    # 绘制曲线
    for key in pointsDic_less10:
        # Normalized Difference between Hotspot and Darkspot NTL radiance (NDHDNTL):
        ori_min = np.min(visNTL_dic[key])
        ori_max = np.max(visNTL_dic[key])
        print(key,"original NTL NDHDNTL value : ", (ori_max - ori_min) / (ori_max + ori_min))
        fit_min = np.min(visNTL_dic_fit[key])
        fit_max = np.max(visNTL_dic_fit[key])
        print(key,"fit NTL NDHDNTL value : ", (fit_max - fit_min) / (fit_max + fit_min))

        # CV 消除平均数不同对两个或多个资料变异程度比较的影响（这里可以消除居住区和商业区等因为用地类型不同，而造成均值不同的情况）
        ori_cv_score = np.std(visNTL_dic[key]) / np.mean(visNTL_dic[key]) * 100
        print(key, "original NTL cv value : ", ori_cv_score)
        fit_cv_score = np.std(visNTL_dic_fit[key]) / np.mean(visNTL_dic_fit[key]) * 100
        print(key, "fit NTL cv value : ", fit_cv_score)

        # 重新组织时间数据
        time_datetime = []
        for i in range(len(visTime_dic[key])):
            datetime_temp = dtime.datetime.strptime(visTime_dic[key][i], "%Y%m%d")
            time_datetime.append(datetime_temp)
        print("time_datetime",time_datetime)
        # plt.tick_params
        plt.figure(figsize=(8, 6))
        # plt.tick_params(labelsize=16)

        # plt.plot(visTime_dic[key], visNTL_dic[key], color='red',label='original')
        # plt.plot_date(time_datetime, visNTL_dic[key], color='red', label='原始时间序列',linestyle='-',marker='')
        plt.plot_date(time_datetime, visNTL_dic[key], color='red', label='original time series', linestyle='-', marker='')
        # plt.plot(visTime_dic_fit[key],visNTL_dic_fit[key],color='green',label='fit(Zenith 0)')
        # plt.plot_date(time_datetime, visNTL_dic_fit[key], color='#0072B2', label='角度归一化后时间序列',linestyle='-',marker='')  # 蓝色#0072B2
        ccc = np.array(visNTL_dic_fit[key]) * 1
        plt.plot_date(time_datetime, ccc, color='#0072B2', label='angle-normalized time series', linestyle='-', marker='')  # 蓝色#0072B2
        # plt.title(r"$\bf{Los\ Angeles\ " + key + "}$",{'size': 16})
        # plt.title(area+r" point "+key, fontproperties="SimHei",fontsize=22)
        plt.title(area + r" " + key, fontproperties="Adobe Gothic Std", fontsize=22)
        # plt.xlabel(u"日期",
        #            fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
        #            fontsize=22)
        plt.xlabel(u"Date",
                   fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf", weight='extra bold'),
                   fontsize=22)
        # plt.ylabel(r"夜光辐亮度", labelpad=15,
        #            fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
        #            fontsize=22)
        plt.ylabel(r"Nighttime Light Radiance", labelpad=15,
                   fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf", weight='extra bold'),
                   fontsize=22)
        # plt.legend(loc="lower right", prop={'size': 22, "family": "SimHei"})
        # plt.legend(loc="upper left", prop={'size': 18, "family": "Adobe Gothic Std"})
        plt.yticks(fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        plt.xticks(fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        plt.tick_params(labelsize=20)
        # plt.xlabel(r"$\bf{VZA(Degree)}$",{'size': 16})
        # plt.ylabel(r"$\bf{DNB\ BRDF-Corrected\ NTL\ Radiance}$",{'size': 16})
        # plt.legend(prop={'size': 16})
        dataFormat = mat.dates.DateFormatter('%Y-%m')
        plt.gca().xaxis.set_major_formatter(dataFormat)
        # plt.xticks(rotation=320)
        # plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))   #更改横坐标的密度
        plt.show()


# 奥尔巴尼效果比较好在R2上
if __name__=="__main__":
    # 需要读取的文件夹路径
    # name_list = ["Arecibo", "Bayamon", "Caguas", "Carolina", "Guayama", "Humacao", "Mayaguez", "Ponce", "SanJuan"]
    name_list = ["Adiyaman",
                  "Aleppo",
                  "Antakya",
                  "Gaziantep",
                  "Kahramanmaras",
                  "Kirikhan",
                  "Latakia",
                  "Samandag"]
    parent_dir = "G:\\postgraduate\\postgraduate_bishe\\"
    time_series_type = "TS_Txt_3_3"
    for name in name_list:
        work_dic = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_"+str(name)
        fit_result_path = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_"+str(name)
        output_dic = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_visFitResult_gradientDescent_1%_1invalid_"+str(name)
        output_params_path = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_fitParams_gradientDescent_1%_1invalid_"+str(name)

        # 读取经过筛选的有效数据（保存在文件中）
        pointNumLngLatMap,pointsDic = readFile(work_dic)

        # 可视化角度和夜光值之间的关系，拟合并归一化，将归一化后的数据保存在文件中
        visScatterAndFitCurve(pointsDic,output_dic,fit_result_path,pointNumLngLatMap, output_params_path)

        # # 读取筛选数据经过角度归一化后的数据（读取之前需要执行visScatterAndFitCurve进行校正）
        # pointNumLngLatMap_fit, pointsDic_fit = readFile(fit_result_path)
        # #
        # # 可视化时间序列，并计算NDHDNTL
        # visTimeSeries(pointsDic, pointsDic_fit,name)