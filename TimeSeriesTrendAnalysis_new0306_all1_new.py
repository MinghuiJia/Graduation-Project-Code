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

def drawPlot(time,value,smooth_value,key_words,restored_time,restored_percent):
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

    # plt.plot(time, smooth_value, color="red", label="NTL estimated",linewidth=2)
    # plt.plot_date(time_datetime, smooth_value, color="red", label="Estimation Results of Black Marble ", linewidth=2,linestyle='-',marker='')
    plt.plot_date(time_datetime, smooth_value, color="red", label="夜光数据估算结果 ", linewidth=2, linestyle='-', marker='')
    # plt.plot(restored_time,restored_percent,color="black",label="official report",linewidth=2)
    # plt.plot_date(restoredtime_datetime, restored_percent, color="black", label="Official Reports", linewidth=2,linestyle='-',marker='')
    plt.plot_date(restoredtime_datetime, restored_percent, color="black", label="官方报道结果", linewidth=2, linestyle='-', marker='')
    # plt.xticks(rotation=320)
    # plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(15))  # 更改横坐标的密度
    # plt.legend(loc='lower right',prop={'size': 22, "family": "Adobe Gothic Std"})
    plt.legend(loc='lower right', prop={'size': 22, "family": "simhei", "weight": "extra bold"})
    # plt.xlabel("date",{'size': 16})
    # plt.ylabel(r"$\bf{Estimated power restoration(\%)}$",{'size': 16})
    plt.xlabel(u"Date", {'size': 22},
               fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=22)
    plt.ylabel(u"power restoration rate", {'size': 22},
               fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=22)
    # plt.title(r"$\bf{"+key_words + "\ 2017/09-2018/04"+"}$",{'size': 16})
    # plt.title(u"飓风玛丽亚袭击后波多黎各的灾后电力恢复", fontproperties="SimHei", fontsize=22)
    plt.yticks(fontproperties=font_manager.FontProperties(
        fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
    plt.xticks(fontproperties=font_manager.FontProperties(
        fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
    plt.tick_params(labelsize=20)
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
    dataFile_Mayaguez = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Mayaguez_more50_wholeSeries_Prophet_afterfit"
    dataFile_Ponce = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Ponce_more50_wholeSeries_Prophet_afterfit"
    dataFile_SanJuan = work_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_SanJuan_more50_wholeSeries_Prophet_afterfit"

    total_value_Arecibo,total_time_Arecibo = getEachDistrictValue(dataFile_Arecibo)
    total_value_Bayamon, total_time_Bayamon = getEachDistrictValue(dataFile_Bayamon)
    total_value_Carolina, total_time_Carolina = getEachDistrictValue(dataFile_Carolina)
    total_value_data, total_time_data = getEachDistrictValue(dataFile_data)
    total_value_Guayama, total_time_Guayama = getEachDistrictValue(dataFile_Guayama)
    total_value_Humacao, total_time_Humacao = getEachDistrictValue(dataFile_Humacao)
    total_value_Mayaguez, total_time_Mayaguez = getEachDistrictValue(dataFile_Mayaguez)
    total_value_Ponce, total_time_Ponce = getEachDistrictValue(dataFile_Ponce)
    total_value_SanJuan, total_time_SanJuan = getEachDistrictValue(dataFile_SanJuan)

    total_value = total_value_Arecibo + total_value_Bayamon + total_value_Carolina + total_value_data + total_value_Guayama + total_value_SanJuan + total_value_Ponce + total_value_Humacao # + total_value_Mayaguez
    total_time = total_time_Arecibo
    # total_value = [x / len(total_value) for x in total_value]

    # # Taking moving average
    # rolling_mean_value = TakingMovingAverage(time,value,10)
    # drawPlot(time,value,rolling_mean_value,key)
    # # break

    # # STL方法
    # value = np.array(value)
    # STLSmooth(value,2)

    # 卡尔曼滤波方法
    smooth_value = Kalman1D(total_value, 0.1)
    smooth_value_new = []
    for k in range(len(smooth_value)):
        smooth_value_new.append(smooth_value[k][0])

    # 计算相对恢复率
    max_value = np.max(smooth_value_new)
    print("max value: ",max_value)
    relative_value_new = []
    for i in range(len(smooth_value_new)):
        relative_value_new.append((smooth_value_new[i] / max_value) * 100)

    # 分别计算三个阶段的恢复率
    show_time = ['2017-09-20', '2017-11-20', '2018-01-20', '2018-03-20']

    stage1_average = 0
    stage2_average = 0
    stage3_average = 0
    stage1_count = 0
    stage2_count = 0
    stage3_count = 0
    statistic_value_est = []
    for i in range(len(total_time)):
        if ('2017-09-19' <= total_time[i] <= '2018-04-01'):
            statistic_value_est.append(smooth_value_new[i])

        if (show_time[0] <= total_time[i] < show_time[1]):
            stage1_average += smooth_value_new[i]
            stage1_count += 1
        elif (show_time[1] <= total_time[i] < show_time[2]):
            stage2_average += smooth_value_new[i]
            stage2_count += 1
        elif (show_time[2] <= total_time[i] <= show_time[3]):
            stage3_average += smooth_value_new[i]
            stage3_count += 1
    stage1_average = stage1_average / stage1_count
    stage2_average = stage2_average / stage2_count
    stage3_average = stage3_average / stage3_count
    print("stage1 %recovery: ",stage1_average/max_value*100)
    print("stage2 %recovery: ",stage2_average/max_value*100)
    print("stage3 %recovery: ",stage3_average/max_value*100)

    stage1_index = total_time.index('2017-11-20')
    stage2_index = total_time.index('2018-01-20')
    stage3_index = total_time.index('2018-03-20')
    a1 = relative_value_new[stage1_index]
    a2 = relative_value_new[stage2_index]
    a3 = relative_value_new[stage3_index]
    print("a1:",a1, "a2:",a2, "a3",a3)

    recovery_rate_min = np.min(relative_value_new)
    stage1_recovery_rate = (relative_value_new[stage1_index] - recovery_rate_min) / (
            100 - recovery_rate_min)
    stage2_recovery_rate = (relative_value_new[stage2_index] - recovery_rate_min) / (
            100 - recovery_rate_min)
    stage3_recovery_rate = (relative_value_new[stage3_index] - recovery_rate_min) / (
            100 - recovery_rate_min)
    print("stage1_recovery_rate:", stage1_recovery_rate,
          "stage2_recovery_rate:", stage2_recovery_rate,
          "stage3_recovery_rate", stage3_recovery_rate)

    print("power loss:",100 - recovery_rate_min)
    NDWE = (1-(stage1_average/max_value))*stage1_count + (1-(stage2_average/max_value))*stage2_count + (1-(stage3_average/max_value))*stage3_count
    print("number of days without electricity: ",NDWE)

    # print(len(statistic_value_est))
    # print(len(restored_percent[:-2]))

    r, p = stats.pearsonr(statistic_value_est, restored_percent[:-2])
    print("Two-sample p-statistic r = ",r, ",p-value = " ,p)

    drawPlot(total_time,total_value,relative_value_new,"Puerto\ Rico",restored_time,restored_percent)

# import numpy as np
# arr = [18,14,56,22,6,64,99,24,16,97]
# # arr = np.divide(arr, 10)
# # print(arr)
# # print(arr[0])
# my_list = [x/10 for x in arr]
# print(my_list)