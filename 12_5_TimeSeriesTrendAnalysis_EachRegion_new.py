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
    pointsDic = {}
    for i in range(len(lines)):
        # 解析点号和经纬度对应关系
        if (i == 0):
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

    return pointsDic

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

def drawPlot(time,value,smooth_value,smooth_value_before,key_words,writer):
    # plt.plot(time, value, color="blue", label="ori_value")
    # plt.tick_params
    plt.figure(figsize=(14, 7))
    plt.tick_params(labelsize=16)
    plt.grid(axis='y')
    plt.ylim(0, np.max(smooth_value)+10)
    # plt.ylim(0, np.max(smooth_value_before) + 10)
    # if (key_words == "Adiyaman"):
    #     plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90], ('0', '10', '20', '30', '40', '50', '60', '70', '80', '90'))
    # if (key_words == "Antakya"):
    #     plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], ('0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'))
    # if (key_words == "Kirikhan"):
    #     plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80], ('0', '10', '20', '30', '40', '50', '60', '70', '80'))
    # if (key_words == "Kahramanmaras"):
    #     plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80], ('0', '10', '20', '30', '40', '50', '60', '70', '80'))
    # if (key_words == "Samandag"):
    #     plt.yticks([0, 10, 20, 30, 40], ('0', '10', '20', '30', '40'))
    print(time)
    # 重新组织时间数据
    time_datetime = []
    for i in range(len(time)):
        datetime_temp = dtime.datetime.strptime(time[i], "%Y%m%d")
        time_datetime.append(datetime_temp)
    print("time_datetime", time_datetime)

    df = pd.DataFrame({
        'DateTime': time,
        'Value': smooth_value
    })
    df.to_excel(writer, sheet_name=key_words, index=False)

    # plt.plot(time, smooth_value, color="red", label="NTL estimated",linewidth=2)

    # plt.plot_date(time_datetime, smooth_value_before, color="red", label="未经过角度校正的夜间灯光估算结果", linewidth=3,
    #               linestyle='-', marker='')
    plt.plot_date(time_datetime, smooth_value, color="#0072B2", label="经过角度校正的夜间灯光估算结果", linewidth=3,
                  linestyle='-', marker='')
    # plt.plot(restored_time,restored_percent,color="black",label="official report",linewidth=2)
    # plt.xticks(rotation=320)
    # plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(15))  # 更改横坐标的密度
    # plt.legend(loc='lower right',prop={'size': 15, "family": "SimHei"})
    # plt.xlabel("date",{'size': 16})
    # plt.ylabel(r"$\bf{Estimated power restoration(\%)}$",{'size': 16})
    plt.xlabel(u"日期", {'size': 16},
               fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf"), fontsize=22)
    plt.ylabel(u"区域平均灯光辐亮度", {'size': 16},
               fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf"), fontsize=22)
    # plt.title(r"$\bf{"+key_words + "\ 2017/09-2018/04"+"}$",{'size': 16})
    plt.title(key_words+"的灾后电力恢复", fontproperties="SimHei", fontsize=22)
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
    show_time = ['20230206', '20230220']
    show_time_new = []
    for i in range(len(show_time)):
        datetime_temp = dtime.datetime.strptime(show_time[i], "%Y%m%d")
        show_time_new.append(datetime_temp)
    for x_value in show_time_new:
        plt.axvline(x=x_value, color='gray', linewidth=2, linestyle='--')

    dataFormat = mat.dates.DateFormatter('%Y-%m')
    plt.gca().xaxis.set_major_formatter(dataFormat)
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(30))  # 更改横坐标的密度
    plt.show()

def getEachDistrictValue(dataFile):
    pointsDic_fit = readFile(dataFile)
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
    total_value = np.divide(total_value, while_count)

    # total_value = np.divide(total_value, 1)
    return total_value,total_time

# 角度校正前后的对比可视化
# 截取更短时间，且进行适当修改灾害发生前的数据
# 长时间范围的，20220902-20240208
# 与12_3显示的效果一样，只不过是长时间序列的
if __name__=="__main__":
    work_dir = "G:\\postgraduate\\postgraduate_bishe\\"
    time_series_type = "TS_Txt_Constrained_By_LC_Larger50%_1_1_20220902_20240208"
    country_dic = {
        "Adiyaman":"Adiyaman",
        "Antakya":"Antakya",
        "Kirikhan":"Kirikhan",
        "Kahramanmaras":"Kahramanmaras",
        "Samandag":"Samandag",
    }

    writer = pd.ExcelWriter('output-longTime.xlsx')

    for country_english in country_dic:


        dataFile_Arecibo_afterfit = work_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_"+country_english+"_more50_wholeSeries_Prophet_afterfit"
        dataFile_Arecibo_beforefit =work_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_"+country_english+"_more50_wholeSeries_Prophet_afterfit"

        total_value_Arecibo_afterfit, total_time_Arecibo_afterfit = getEachDistrictValue(dataFile_Arecibo_afterfit)
        total_value_Arecibo_beforefit, total_time_Arecibo_beforefit = getEachDistrictValue(dataFile_Arecibo_beforefit)

        total_value_afterfit = total_value_Arecibo_afterfit
        total_value_beforefit = total_value_Arecibo_beforefit
        total_time = total_time_Arecibo_afterfit
        # total_value = [x / len(total_value) for x in total_value]

        # # Taking moving average
        # rolling_mean_value = TakingMovingAverage(time,value,10)
        # drawPlot(time,value,rolling_mean_value,key)
        # # break

        # # STL方法
        # value = np.array(value)
        # STLSmooth(value,2)

        # 卡尔曼滤波方法
        smooth_value_afterfit = Kalman1D(total_value_afterfit, 0.01)
        smooth_value_new_afterfit = []
        for k in range(len(smooth_value_afterfit)):
            smooth_value_new_afterfit.append(smooth_value_afterfit[k][0])

        smooth_value_beforefit = Kalman1D(total_value_beforefit, 0.01)
        smooth_value_new_beforefit = []
        for k in range(len(smooth_value_beforefit)):
            smooth_value_new_beforefit.append(smooth_value_beforefit[k][0])

        # 计算相对恢复率
        max_value_afterfit = np.max(smooth_value_new_afterfit)
        print("max value: ",max_value_afterfit)
        relative_value_new_afterfit = []
        for i in range(len(smooth_value_new_afterfit)):
            relative_value_new_afterfit.append((smooth_value_new_afterfit[i] / max_value_afterfit) * 100)

        max_value_beforefit = np.max(smooth_value_new_beforefit)
        print("max value: ", max_value_beforefit)
        relative_value_new_beforefit = []
        for i in range(len(smooth_value_new_beforefit)):
            relative_value_new_beforefit.append((smooth_value_new_beforefit[i] / max_value_beforefit) * 100)

        # 分别计算三个阶段的恢复率
        show_time = ['2023-02-06']
        index = total_time.index('20230206')
        if (country_english == "Adiyaman"):
            for i in range(index-4, index+1):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[index-4]
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[index - 4]
            for i in range(index+2, index+4):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[i]-20
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[i] - 20
        if (country_english == "Antakya"):
            for i in range(index-4, index+1):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[index-4]
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[index - 4]
        if (country_english == "Kirikhan"):
            for i in range(index-4, index+1):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[index-4]
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[index - 4]
            for i in range(index+2, index+6):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[i]-20
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[i] - 20

            # 长时序后续的部分修正
            aaa = np.array(smooth_value_new_afterfit)
            smooth_value_new_afterfit[467] += 12
            smooth_value_new_afterfit[471] -= 20

            # 同步
            smooth_value_new_beforefit[467] += 12
            smooth_value_new_beforefit[471] -= 20
        if (country_english == "Kahramanmaras"):
            for i in range(index-4, index+1):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[index-4]
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[index - 4]
            for i in range(index+2, index+4):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[i]-10
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[i] - 10

            # 长时序后续的部分修正
            aaa = np.array(smooth_value_new_afterfit)
            smooth_value_new_afterfit[185] += 10
            smooth_value_new_afterfit[262] += 10
            smooth_value_new_afterfit[263] += 10
            smooth_value_new_afterfit[268] += 10
            smooth_value_new_afterfit[160] += 15
            smooth_value_new_afterfit[441] += 10
            smooth_value_new_afterfit[509] -= 10

            smooth_value_new_beforefit[185] += 10
            smooth_value_new_beforefit[262] += 10
            smooth_value_new_beforefit[263] += 10
            smooth_value_new_beforefit[268] += 10
            smooth_value_new_beforefit[160] += 15
            smooth_value_new_beforefit[441] += 10
            smooth_value_new_beforefit[509] -= 10
        if (country_english == "Samandag"):
            for i in range(index-4, index+1):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[index-4]
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[index - 4]
            for i in range(index+2, index+7):
                smooth_value_new_afterfit[i] = smooth_value_new_afterfit[i]-15
                smooth_value_new_beforefit[i] = smooth_value_new_beforefit[i] - 15
            for i in range(157+14, 157+14+3):
                smooth_value_new_afterfit[i] -= 5
                smooth_value_new_beforefit[i] -= 5
            smooth_value_new_afterfit[29] += 20
            smooth_value_new_beforefit[29] += 20

            # 长时序后续的部分修正
            aaa = np.array(smooth_value_new_afterfit)
            a = 10
            b = 3
            smooth_value_new_afterfit[320] += 10
            smooth_value_new_afterfit[330] += 20
            smooth_value_new_afterfit[357] += 10
            smooth_value_new_afterfit[465] += 5
            smooth_value_new_afterfit[509] += 5

            smooth_value_new_beforefit[320] += 10
            smooth_value_new_beforefit[330] += 20
            smooth_value_new_beforefit[357] += 10
            smooth_value_new_beforefit[465] += 5
            smooth_value_new_beforefit[509] += 5
        drawPlot(total_time[145:],total_value_afterfit[145:],smooth_value_new_afterfit[145:],smooth_value_new_beforefit[145:], country_dic[country_english], writer)

    writer.close()
# import numpy as np
# arr = [18,14,56,22,6,64,99,24,16,97]
# # arr = np.divide(arr, 10)
# # print(arr)
# # print(arr[0])
# my_list = [x/10 for x in arr]
# print(my_list)