import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from statsmodels.tsa.seasonal import STL
import pandas as pd
from pykalman import KalmanFilter
import numpy as np
import csv
import scipy.stats as stats
import scipy.optimize as opt
from matplotlib import font_manager
import datetime as dtime
import matplotlib as mat

# 读取并解析文件
def readFile(filePath):
    f = open(filePath,'r')
    lines = f.readlines()
    pointNumLngLatMap = {}
    pointsDic = {}
    for i in range(len(lines)):
        # 解析点号和经纬度对应关系
        if (i == 0):
            points_list = lines[i].split(";")
            for j in range(len(points_list)):
                temp_list = points_list[j].split(":")
                lnglat = temp_list[1].split(",")
                pointNumLngLatMap[temp_list[0]] = [float(lnglat[0]),float(lnglat[1])]
        # 这一行为数据存储格式，需要跳过
        elif (i == 1):
            pass
        # 解析数据
        else:
            temp_list = lines[i].split(":")
            pointNum = temp_list[0]
            pointsDic[pointNum] = []
            info_list = temp_list[1].split(";")
            for k in range(len(info_list)):
                value_list = info_list[k].split(",")
                pointsDic[pointNum].append([float(value_list[1]),value_list[0]])
    #     # print(lines[i])
    # print(pointNumLngLatMap)
    # print(pointsDic)
    return pointNumLngLatMap,pointsDic

def Kalman1D(observations,damping=1):
    # To return the smoothed time series data
    observation_covariance = damping
    initial_value_guess = observations[0]
    transition_matrix = 1
    transition_covariance = 0.1
    # initial_value_guess
    kf = KalmanFilter(
            initial_state_mean=initial_value_guess,
            initial_state_covariance=observation_covariance,
            observation_covariance=observation_covariance,
            transition_covariance=transition_covariance,
            transition_matrices=transition_matrix
        )
    pred_state, state_cov = kf.smooth(observations)
    return pred_state

def STLSmooth(arr,period):
    stl = STL(arr, period=period, robust=True)
    res_robust = stl.fit()
    fig = res_robust.plot()
    show_time = ['2015-04-25', '2015-05-12']
    for x_value in show_time:
        plt.axvline(x=x_value, color='green', linewidth=1, linestyle='--')
    plt.show()

def TakingMovingAverage(x,y,window):
    column_name = ['date', 'value']
    df = pd.DataFrame(np.vstack((x, y)).T, columns=column_name)
    df = df.set_index('date')
    rolling = df.rolling(window=window)
    rolling_mean = rolling.mean()
    return rolling_mean

def drawPlot(time,
             value_arecibo,
             value_bayamon,
             value_carolina,
             value_ponce,
             value_sanjuan,
             value_caguas,
             value_guayama,
             value_humacao,key_words,restored_time,restored_percent):
    # plt.plot(time, value, color="blue", label="ori_value")
    # plt.tick_params
    plt.figure(figsize=(12, 9))
    plt.tick_params(labelsize=16)
    plt.grid(axis='y')
    plt.yticks([0,20,40,60,80,100], ('0%', '20%', '40%', '60%','80%','100%'))
    print(time)
    print(restored_time)
    # 重新组织时间数据
    time_datetime = []
    for i in range(len(time)):
        datetime_temp = dtime.datetime.strptime(time[i], "%Y-%m-%d")
        time_datetime.append(datetime_temp)
    print("time_datetime", time_datetime)
    # 重新组织时间数据
    restoredtime_datetime = []
    for i in range(len(restored_time)):
        restoreddatetime_temp = dtime.datetime.strptime(restored_time[i], "%Y-%m-%d")
        restoredtime_datetime.append(restoreddatetime_temp)
    print("time_datetime", restoredtime_datetime)

    # plt.figure(figsize=(8, 6))
    # plt.plot(time, smooth_value, color="red", label="NTL estimated",linewidth=2)
    # plt.plot_date(time_datetime, value_arecibo, color="black", label="Arecibo", linewidth=2,
    #               linestyle='-',marker='', markersize=7, markevery=8)
    # plt.plot_date(time_datetime, value_bayamon, color="black", label="Bayamon", linewidth=2,
    #               linestyle='--', marker='', markersize=7, markevery=8)
    # plt.plot_date(time_datetime, value_carolina, color="black", label="Carolina", linewidth=2,
    #               linestyle='-.', marker='', markersize=7, markevery=8)
    #
    # plt.plot_date(time_datetime, value_caguas, color="darkorange", label="Caguas", linewidth=2,
    #               linestyle='-',marker='s', markersize=7, markevery=8)
    # plt.plot_date(time_datetime, value_guayama, color="darkorange", label="Guayama", linewidth=2,
    #               linestyle='-', marker='o', markersize=7, markevery=8)
    # plt.plot_date(time_datetime, value_humacao, color='darkorange', label="Humacao", linewidth=2,
    #               linestyle='-', marker='*', markersize=9, markevery=8)
    #
    # plt.plot_date(time_datetime[0], 0, color="green", linewidth=0,
    #               linestyle='', marker='')
    #
    # plt.plot_date(time_datetime, value_ponce, color="#0072B2", label="Ponce", linewidth=2,
    #               linestyle='-',marker='s', markersize=7, markevery=8)
    # plt.plot_date(time_datetime, value_sanjuan, color="#0072B2", label="SanJuan", linewidth=2,
    #               linestyle='-', marker='o', markersize=7, markevery=8)
    plt.plot_date(time_datetime, value_arecibo, color="black", label="阿雷西沃", linewidth=2,
                  linestyle='-', marker='', markersize=7, markevery=8)
    plt.plot_date(time_datetime, value_bayamon, color="black", label="巴亚蒙", linewidth=2,
                  linestyle='--', marker='', markersize=7, markevery=8)
    plt.plot_date(time_datetime, value_carolina, color="black", label="卡罗利纳", linewidth=2,
                  linestyle='-.', marker='', markersize=7, markevery=8)

    plt.plot_date(time_datetime, value_caguas, color="darkorange", label="卡瓜斯", linewidth=2,
                  linestyle='-', marker='s', markersize=7, markevery=8)
    plt.plot_date(time_datetime, value_guayama, color="darkorange", label="瓜亚马", linewidth=2,
                  linestyle='-', marker='o', markersize=7, markevery=8)
    plt.plot_date(time_datetime, value_humacao, color='darkorange', label="乌马考", linewidth=2,
                  linestyle='-', marker='*', markersize=9, markevery=8)

    plt.plot_date(time_datetime[0], 0, color="green", linewidth=0,
                  linestyle='', marker='')

    plt.plot_date(time_datetime, value_ponce, color="#0072B2", label="庞塞", linewidth=2,
                  linestyle='-', marker='s', markersize=7, markevery=8)
    plt.plot_date(time_datetime, value_sanjuan, color="#0072B2", label="圣胡安", linewidth=2,
                  linestyle='-', marker='o', markersize=7, markevery=8)
    # plt.plot(restored_time,restored_percent,color="black",label="official report",linewidth=2)
    # plt.plot_date(restoredtime_datetime, restored_percent, color="black", label="Official Reports", linewidth=2,linestyle='-',marker='')
    # plt.xticks(rotation=320)
    # plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(15))  # 更改横坐标的密度
    # plt.legend(loc='lower right',prop={'size': 14, "family": "Adobe Gothic Std"})
    plt.legend(loc='lower right', prop={'size': 14, "family": "simhei", "weight": "extra bold"})
    # plt.xlabel("date",{'size': 16})
    # plt.ylabel(r"$\bf{Estimated power restoration(\%)}$",{'size': 16})
    plt.xlabel(u"Date", {'size': 10},
               fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=22)
    plt.ylabel(u"power restoration rate", {'size': 10},
               fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=22)
    # plt.title(r"$\bf{"+key_words + "\ 2017/09-2018/04"+"}$",{'size': 16})
    # plt.title(u"飓风玛丽亚袭击后波多黎各的灾后电力恢复", fontproperties="SimHei", fontsize=22)
    plt.yticks(fontproperties=font_manager.FontProperties(
        fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
    plt.xticks(fontproperties=font_manager.FontProperties(
        fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
    plt.tick_params(labelsize=16)
    # # 绘制竖线
    # show_time = ['2015-04-25', '2015-05-12']
    # for x_value in show_time:
    #     plt.axvline(x=x_value, color='green', linewidth=1, linestyle='--')

    # 绘制竖线
    show_time = ['2017-09-20', '2017-11-20', '2018-01-20', '2018-03-20']
    show_time_new = []
    for i in range(len(show_time)):
        datetime_temp = dtime.datetime.strptime(show_time[i], "%Y-%m-%d")
        show_time_new.append(datetime_temp)
    for x_value in show_time_new:
        plt.axvline(x=x_value, color='black', linewidth=1, linestyle='-')

    dataFormat = mat.dates.DateFormatter('%Y-%m')
    plt.gca().xaxis.set_major_formatter(dataFormat)
    plt.show()

def readCSV(csvFile):
    line_count = 0
    time_list = []
    value_list = []
    with open(csvFile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if (line_count == 0):
                line_count += 1
                continue
            time = row[0].replace('/','-')
            time_split = time.split('-')
            if (len(time_split[1]) == 1 and len(time_split[2]) != 1):
                time = time_split[0]+"-0"+time_split[1]+"-"+time_split[2]
            elif (len(time_split[2]) == 1 and len(time_split[1]) != 1):
                time = time_split[0] + "-" + time_split[1] + "-0" + time_split[2]
            elif (len(time_split[1]) == 1 and len(time_split[2]) == 1):
                time = time_split[0] + "-0" + time_split[1] + "-0" + time_split[2]
            time_list.append(time)
            value_list.append(float(row[1]))
            line_count += 1
    # print(time_list)
    # print(value_list)
    return time_list,value_list

def getEachDistrictValue(dataFile):
    pointNumLngLatMap_fit, pointsDic_fit = readFile(dataFile)
    total_value = []
    total_time = []
    while_count = 0
    for key in pointsDic_fit:
        if while_count == 0:
            for i in range(len(pointsDic_fit[key])):
                total_time.append(pointsDic_fit[key][i][1])
                total_value.append(pointsDic_fit[key][i][0])
        else:
            for i in range(len(pointsDic_fit[key])):
                total_value[i] += pointsDic_fit[key][i][0]

        while_count += 1

    # total_value = np.divide(total_value, len(total_value))

    total_value = np.divide(total_value, 1)
    return total_value,total_time

if __name__=="__main__":
    work_dir = "D:\\VZA_Article\\data\\event_shortTime\\id18_20170901_20180401\\new_method\\"
    csvFile = work_dir + "restored_data.csv"
    restored_time, restored_percent = readCSV(csvFile)

    dataFile_Arecibo = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Arecibo_more50_wholeSeries_Prophet_afterfit"
    dataFile_Bayamon = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Bayamon_more50_wholeSeries_Prophet_afterfit"
    dataFile_Carolina = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Carolina_more50_wholeSeries_Prophet_afterfit"
    dataFile_data = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Caguas_more50_wholeSeries_Prophet_afterfit"
    dataFile_Guayama = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Guayama_more50_wholeSeries_Prophet_afterfit"
    dataFile_Humacao = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Humacao_more50_wholeSeries_Prophet_afterfit"
    # dataFile_Mayaguez = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Mayaguez_more50_wholeSeries_Prophet_afterfit"
    dataFile_Ponce = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Ponce_more50_wholeSeries_Prophet_afterfit"
    dataFile_SanJuan = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_SanJuan_more50_wholeSeries_Prophet_afterfit"

    total_value_Arecibo,total_time_Arecibo = getEachDistrictValue(dataFile_Arecibo)
    total_value_Bayamon, total_time_Bayamon = getEachDistrictValue(dataFile_Bayamon)
    total_value_Carolina, total_time_Carolina = getEachDistrictValue(dataFile_Carolina)
    total_value_data, total_time_data = getEachDistrictValue(dataFile_data)
    total_value_Guayama, total_time_Guayama = getEachDistrictValue(dataFile_Guayama)
    total_value_Humacao, total_time_Humacao = getEachDistrictValue(dataFile_Humacao)
    # total_value_Mayaguez, total_time_Mayaguez = getEachDistrictValue(dataFile_Mayaguez)
    total_value_Ponce, total_time_Ponce = getEachDistrictValue(dataFile_Ponce)
    total_value_SanJuan, total_time_SanJuan = getEachDistrictValue(dataFile_SanJuan)

    # total_value = total_value_Arecibo + total_value_Bayamon + total_value_Carolina + total_value_data + total_value_Guayama + total_value_SanJuan + total_value_Ponce + total_value_Humacao # + total_value_Mayaguez
    total_time = total_time_data
    # total_value = [x / len(total_value) for x in total_value]

    # # Taking moving average
    # rolling_mean_value = TakingMovingAverage(time,value,10)
    # drawPlot(time,value,rolling_mean_value,key)
    # # break

    # # STL方法
    # value = np.array(value)
    # STLSmooth(value,2)
    # 卡尔曼滤波方法

    smooth_value_arecibo = Kalman1D(total_value_Arecibo, 0.1)
    smooth_value_new_arecibo = []
    for k in range(len(smooth_value_arecibo)):
        smooth_value_new_arecibo.append(smooth_value_arecibo[k][0])

    smooth_value_bayamon = Kalman1D(total_value_Bayamon, 0.1)
    smooth_value_new_bayamon = []
    for k in range(len(smooth_value_bayamon)):
        smooth_value_new_bayamon.append(smooth_value_bayamon[k][0])

    smooth_value_carolina = Kalman1D(total_value_Carolina, 0.1)
    smooth_value_new_carolina = []
    for k in range(len(smooth_value_carolina)):
        smooth_value_new_carolina.append(smooth_value_carolina[k][0])

    smooth_value_ponce = Kalman1D(total_value_Ponce, 0.1)
    smooth_value_new_ponce = []
    for k in range(len(smooth_value_ponce)):
        smooth_value_new_ponce.append(smooth_value_ponce[k][0])

    smooth_value_sanjuan = Kalman1D(total_value_SanJuan, 0.1)
    smooth_value_new_sanjuan = []
    for k in range(len(smooth_value_sanjuan)):
        smooth_value_new_sanjuan.append(smooth_value_sanjuan[k][0])

    smooth_value_caguas = Kalman1D(total_value_data, 0.1)
    smooth_value_new_caguas = []
    for k in range(len(smooth_value_caguas)):
        smooth_value_new_caguas.append(smooth_value_caguas[k][0])

    smooth_value_guayama = Kalman1D(total_value_Guayama, 0.1)
    smooth_value_new_guayama = []
    for k in range(len(smooth_value_guayama)):
        smooth_value_new_guayama.append(smooth_value_guayama[k][0])

    smooth_value_humacao = Kalman1D(total_value_Humacao, 0.1)
    smooth_value_new_humacao = []
    for k in range(len(smooth_value_humacao)):
        smooth_value_new_humacao.append(smooth_value_humacao[k][0])

    # 计算相对恢复率
    max_value_arecibo = np.max(smooth_value_new_arecibo)
    print("max value: ", max_value_arecibo)
    relative_value_new_arecibo = []
    for i in range(len(smooth_value_new_arecibo)):
        relative_value_new_arecibo.append((smooth_value_new_arecibo[i] / max_value_arecibo) * 100)

    max_value_bayamon = np.max(smooth_value_new_bayamon)
    print("max value: ", max_value_bayamon)
    relative_value_new_bayamon = []
    for i in range(len(smooth_value_new_bayamon)):
        relative_value_new_bayamon.append((smooth_value_new_bayamon[i] / max_value_bayamon) * 100)

    max_value_carolina = np.max(smooth_value_new_carolina)
    print("max value: ", max_value_carolina)
    relative_value_new_carolina = []
    for i in range(len(smooth_value_new_carolina)):
        relative_value_new_carolina.append((smooth_value_new_carolina[i] / max_value_carolina) * 100)

    max_value_ponce = np.max(smooth_value_new_ponce)
    print("max value: ", max_value_ponce)
    relative_value_new_ponce = []
    for i in range(len(smooth_value_new_ponce)):
        relative_value_new_ponce.append((smooth_value_new_ponce[i] / max_value_ponce) * 100)

    max_value_sanjuan = np.max(smooth_value_new_sanjuan)
    print("max value: ", max_value_sanjuan)
    relative_value_new_sanjuan = []
    for i in range(len(smooth_value_new_sanjuan)):
        relative_value_new_sanjuan.append((smooth_value_new_sanjuan[i] / max_value_sanjuan) * 100)

    max_value_caguas = np.max(smooth_value_new_caguas)
    print("max value: ", max_value_caguas)
    relative_value_new_caguas = []
    for i in range(len(smooth_value_new_caguas)):
        relative_value_new_caguas.append((smooth_value_new_caguas[i] / max_value_caguas) * 100)

    max_value_caguas = np.max(smooth_value_new_caguas)
    print("max value: ",max_value_caguas)
    relative_value_new_caguas = []
    for i in range(len(smooth_value_new_caguas)):
        relative_value_new_caguas.append((smooth_value_new_caguas[i] / max_value_caguas) * 100)

    max_value_guayama = np.max(smooth_value_new_guayama)
    print("max value: ", max_value_guayama)
    relative_value_new_guayama = []
    for i in range(len(smooth_value_new_guayama)):
        relative_value_new_guayama.append((smooth_value_new_guayama[i] / max_value_guayama) * 100)

    max_value_humacao = np.max(smooth_value_new_humacao)
    print("max value: ", max_value_humacao)
    relative_value_new_humacao = []
    for i in range(len(smooth_value_new_humacao)):
        relative_value_new_humacao.append((smooth_value_new_humacao[i] / max_value_humacao) * 100)

    # 分别计算三个阶段的恢复率
    show_time = ['2017-09-20', '2017-11-20', '2018-01-20', '2018-03-20']


    drawPlot(total_time,
             relative_value_new_arecibo,
             relative_value_new_bayamon,
             relative_value_new_carolina,
             relative_value_new_ponce,
             relative_value_new_sanjuan,
             relative_value_new_caguas,
             relative_value_new_guayama,
             relative_value_new_humacao,"Puerto\ Rico",restored_time,restored_percent)

# import numpy as np
# arr = [18,14,56,22,6,64,99,24,16,97]
# # arr = np.divide(arr, 10)
# # print(arr)
# # print(arr[0])
# my_list = [x/10 for x in arr]
# print(my_list)