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
import seaborn as sns

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

    # plt.plot(time, smooth_value, color="red", label="NTL estimated",linewidth=2)
    plt.plot_date(time_datetime, value_arecibo, color="red", label="Arecibo", linewidth=2,
                  linestyle='-', marker='')
    plt.plot_date(time_datetime, value_bayamon, color="red", label="Bayamon", linewidth=2,
                  linestyle='--', marker='')
    plt.plot_date(time_datetime, value_carolina, color="red", label="Carolina", linewidth=2,
                  linestyle='-.', marker='')

    plt.plot_date(time_datetime, value_caguas, color="green", label="Caguas", linewidth=2,
                  linestyle='-',marker='')
    plt.plot_date(time_datetime, value_guayama, color="green", label="Guayama", linewidth=2,
                  linestyle='--', marker='')
    plt.plot_date(time_datetime, value_humacao, color='green', label="Humacao", linewidth=2,
                  linestyle='-.', marker='')

    plt.plot_date(time_datetime[0], 0, color="green", linewidth=0,
                  linestyle='', marker='')

    plt.plot_date(time_datetime, value_ponce, color="#0072B2", label="Ponce", linewidth=2,
                  linestyle='-', marker='')
    plt.plot_date(time_datetime, value_sanjuan, color="#0072B2", label="SanJuan", linewidth=2,
                  linestyle='--', marker='')
    # plt.plot(restored_time,restored_percent,color="black",label="official report",linewidth=2)
    # plt.plot_date(restoredtime_datetime, restored_percent, color="black", label="Official Reports", linewidth=2,linestyle='-',marker='')
    # plt.xticks(rotation=320)
    # plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(15))  # 更改横坐标的密度
    plt.legend(loc='lower right',prop={'size': 16, "family": "Adobe Gothic Std"})
    # plt.xlabel("date",{'size': 16})
    # plt.ylabel(r"$\bf{Estimated power restoration(\%)}$",{'size': 16})
    plt.xlabel(u"Date", {'size': 16},
               fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=22)
    plt.ylabel(u"power restoration rate", {'size': 16},
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

def getEachDistrictHist(dataFile, selectTime):
    pointNumLngLatMap_fit, pointsDic_fit = readFile(dataFile)
    total_value = []
    total_time = []
    while_count = 0
    oneDayAllPixelsValue = []
    for key in pointsDic_fit:
        for i in range(len(pointsDic_fit[key])):
            if (pointsDic_fit[key][i][1] == selectTime):
                oneDayAllPixelsValue.append(pointsDic_fit[key][i][0])

        # if while_count == 0:
        #     for i in range(len(pointsDic_fit[key])):
        #         total_time.append(pointsDic_fit[key][i][1])
        #         total_value.append(pointsDic_fit[key][i][0])
        # else:
        #     for i in range(len(pointsDic_fit[key])):
        #         total_value[i] += pointsDic_fit[key][i][0]

        while_count += 1

    # total_value = np.divide(total_value, len(total_value))

    return oneDayAllPixelsValue



def draw_distribution_histogram(nums,nums2, is_hist=True, is_kde=True, is_rug=False, is_vertical=False, is_norm_hist=True):
    """

    bins: 设置直方图条形的数目
    is_hist: 是否绘制直方图
    is_kde: 是否绘制核密度图
    is_rug: 是否绘制生成观测数值的小细条
    is_vertical: 如果为True，观察值在y轴上
    is_norm_hist: 如果为True，直方图高度显示一个密度而不是一个计数，如果kde设置为True，则此参数一定为True
    """
    sns.set()  # 切换到sns的默认运行配置
    # sns.distplot(nums, bins=range(0,100,2), hist=is_hist, kde=is_kde, rug=is_rug,
    #              hist_kws={"color": "steelblue"}, kde_kws={"color": "purple"},
    #              vertical=is_vertical, norm_hist=is_norm_hist, label="Bayamon")
    sns.distplot(nums2, bins=range(0,100,2), hist=is_hist, kde=is_kde, rug=is_rug,
                 hist_kws={"color": "steelblue"}, kde_kws={"color": "purple"},
                 vertical=is_vertical, norm_hist=is_norm_hist, label="SanJuan")

    # sns.distplot(nums2, bins=range(0, 100, 2), hist=is_hist, kde=is_kde, rug=is_rug,
    #              hist_kws={"color": "red"}, kde_kws={"color": "red"},
    #              vertical=is_vertical, norm_hist=is_norm_hist, label="Bayamon Post")

    # plt.xlim(0, 100)
    plt.xlim(0, 60)
    # 添加标题
    # plt.title("Distribution")
    # 添加x轴和y轴标签
    # plt.legend(loc='upper right', prop={'size': 14, "family": "Adobe Gothic Std"})
    plt.xlabel(u"Radiance", {'size': 10},
               fontproperties=font_manager.FontProperties(
                   fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=18)
    plt.ylabel(u"Frequency", {'size': 10},
               fontproperties=font_manager.FontProperties(
                   fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=18)
    plt.yticks(fontproperties=font_manager.FontProperties(
        fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
    plt.xticks(fontproperties=font_manager.FontProperties(
        fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
    plt.tight_layout()  # 处理显示不完整的问题
    plt.tick_params(labelsize=14)
    # plt.savefig(path, dpi=300)
    plt.show()

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

    oneDayAllPixelsValueBayamonPre = getEachDistrictHist(dataFile_Bayamon, '2017-09-02')
    oneDayAllPixelsValueBayamonPost = getEachDistrictHist(dataFile_Bayamon, '2017-09-28')
    oneDayAllPixelsValueBayamonPost2 = getEachDistrictHist(dataFile_Bayamon, '2017-11-14')

    oneDayAllPixelsValueSanJuanPre = getEachDistrictHist(dataFile_SanJuan, '2017-09-02')
    oneDayAllPixelsValueSanJuanPost = getEachDistrictHist(dataFile_SanJuan, '2017-09-28')
    oneDayAllPixelsValueSanJuanPost2 = getEachDistrictHist(dataFile_SanJuan, '2017-11-14')

    draw_distribution_histogram(oneDayAllPixelsValueBayamonPre,oneDayAllPixelsValueBayamonPost2, True, False)
    # draw_distribution_histogram(oneDayAllPixelsValueBayamonPost, oneDayAllPixelsValueSanJuanPost, True, False)

    # draw_distribution_histogram(oneDayAllPixelsValueBayamonPre, oneDayAllPixelsValueBayamonPost, True, False)
    # draw_distribution_histogram(oneDayAllPixelsValueBayamonPost, oneDayAllPixelsValueSanJuanPost, True, False)

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

    time1 = '2017-09-02'
    time2 = '2017-09-18'
    time3 = '2017-09-28'
    time4 = '2017-11-14'

    time5 = '2017-09-02'
    time6 = '2017-09-18'

    index1 = total_time.index(time1)
    index2 = total_time.index(time2)
    index3 = total_time.index(time3)
    index4 = total_time.index(time4)
    index5 = total_time.index(time5)
    index6 = total_time.index(time6)

    print("SanJuan: ",
          total_value_SanJuan[index1], total_value_SanJuan[index2],
          total_value_SanJuan[index3], total_value_SanJuan[index4])
    print("Bayamon: ",
          total_value_Bayamon[index5], total_value_Bayamon[index6],
          total_value_Bayamon[index3], total_value_Bayamon[index4])

    # 绘制直方图，灾前一张，灾后一张，8个区域的


#     smooth_value_arecibo = Kalman1D(total_value_Arecibo, 0.1)
#     smooth_value_new_arecibo = []
#     for k in range(len(smooth_value_arecibo)):
#         smooth_value_new_arecibo.append(smooth_value_arecibo[k][0])
#
#     smooth_value_bayamon = Kalman1D(total_value_Bayamon, 0.1)
#     smooth_value_new_bayamon = []
#     for k in range(len(smooth_value_bayamon)):
#         smooth_value_new_bayamon.append(smooth_value_bayamon[k][0])
#
#     smooth_value_carolina = Kalman1D(total_value_Carolina, 0.1)
#     smooth_value_new_carolina = []
#     for k in range(len(smooth_value_carolina)):
#         smooth_value_new_carolina.append(smooth_value_carolina[k][0])
#
#     smooth_value_ponce = Kalman1D(total_value_Ponce, 0.1)
#     smooth_value_new_ponce = []
#     for k in range(len(smooth_value_ponce)):
#         smooth_value_new_ponce.append(smooth_value_ponce[k][0])
#
#     smooth_value_sanjuan = Kalman1D(total_value_SanJuan, 0.1)
#     smooth_value_new_sanjuan = []
#     for k in range(len(smooth_value_sanjuan)):
#         smooth_value_new_sanjuan.append(smooth_value_sanjuan[k][0])
#
#     smooth_value_caguas = Kalman1D(total_value_data, 0.1)
#     smooth_value_new_caguas = []
#     for k in range(len(smooth_value_caguas)):
#         smooth_value_new_caguas.append(smooth_value_caguas[k][0])
#
#     smooth_value_guayama = Kalman1D(total_value_Guayama, 0.1)
#     smooth_value_new_guayama = []
#     for k in range(len(smooth_value_guayama)):
#         smooth_value_new_guayama.append(smooth_value_guayama[k][0])
#
#     smooth_value_humacao = Kalman1D(total_value_Humacao, 0.1)
#     smooth_value_new_humacao = []
#     for k in range(len(smooth_value_humacao)):
#         smooth_value_new_humacao.append(smooth_value_humacao[k][0])
#
#     # 计算相对恢复率
#     max_value_arecibo = np.max(smooth_value_new_arecibo)
#     print("max value: ", max_value_arecibo)
#     relative_value_new_arecibo = []
#     for i in range(len(smooth_value_new_arecibo)):
#         relative_value_new_arecibo.append((smooth_value_new_arecibo[i] / max_value_arecibo) * 100)
#
#     max_value_bayamon = np.max(smooth_value_new_bayamon)
#     print("max value: ", max_value_bayamon)
#     relative_value_new_bayamon = []
#     for i in range(len(smooth_value_new_bayamon)):
#         relative_value_new_bayamon.append((smooth_value_new_bayamon[i] / max_value_bayamon) * 100)
#
#     max_value_carolina = np.max(smooth_value_new_carolina)
#     print("max value: ", max_value_carolina)
#     relative_value_new_carolina = []
#     for i in range(len(smooth_value_new_carolina)):
#         relative_value_new_carolina.append((smooth_value_new_carolina[i] / max_value_carolina) * 100)
#
#     max_value_ponce = np.max(smooth_value_new_ponce)
#     print("max value: ", max_value_ponce)
#     relative_value_new_ponce = []
#     for i in range(len(smooth_value_new_ponce)):
#         relative_value_new_ponce.append((smooth_value_new_ponce[i] / max_value_ponce) * 100)
#
#     max_value_sanjuan = np.max(smooth_value_new_sanjuan)
#     print("max value: ", max_value_sanjuan)
#     relative_value_new_sanjuan = []
#     for i in range(len(smooth_value_new_sanjuan)):
#         relative_value_new_sanjuan.append((smooth_value_new_sanjuan[i] / max_value_sanjuan) * 100)
#
#     max_value_caguas = np.max(smooth_value_new_caguas)
#     print("max value: ", max_value_caguas)
#     relative_value_new_caguas = []
#     for i in range(len(smooth_value_new_caguas)):
#         relative_value_new_caguas.append((smooth_value_new_caguas[i] / max_value_caguas) * 100)
#
#     max_value_caguas = np.max(smooth_value_new_caguas)
#     print("max value: ",max_value_caguas)
#     relative_value_new_caguas = []
#     for i in range(len(smooth_value_new_caguas)):
#         relative_value_new_caguas.append((smooth_value_new_caguas[i] / max_value_caguas) * 100)
#
#     max_value_guayama = np.max(smooth_value_new_guayama)
#     print("max value: ", max_value_guayama)
#     relative_value_new_guayama = []
#     for i in range(len(smooth_value_new_guayama)):
#         relative_value_new_guayama.append((smooth_value_new_guayama[i] / max_value_guayama) * 100)
#
#     max_value_humacao = np.max(smooth_value_new_humacao)
#     print("max value: ", max_value_humacao)
#     relative_value_new_humacao = []
#     for i in range(len(smooth_value_new_humacao)):
#         relative_value_new_humacao.append((smooth_value_new_humacao[i] / max_value_humacao) * 100)
#
#     dis_curr_time_index = total_time.index("2017-09-20")
#     dis_stage1_time_index = total_time.index("2017-11-20")
#
#     for i in range(dis_curr_time_index):
#         print(i)
#     print("********")
#     for i in range(dis_curr_time_index, dis_stage1_time_index):
#         print(i,total_time[i])
#     # 分别计算三个阶段的恢复率
#     show_time = ['2017-09-20', '2017-11-20', '2018-01-20', '2018-03-20']
#
#
#     # drawPlot(total_time,
#     #          relative_value_new_arecibo,
#     #          relative_value_new_bayamon,
#     #          relative_value_new_carolina,
#     #          relative_value_new_ponce,
#     #          relative_value_new_sanjuan,
#     #          relative_value_new_caguas,
#     #          relative_value_new_guayama,
#     #          relative_value_new_humacao,"Puerto\ Rico",restored_time,restored_percent)
#
# # import numpy as np
# # arr = [18,14,56,22,6,64,99,24,16,97]
# # # arr = np.divide(arr, 10)
# # # print(arr)
# # # print(arr[0])
# # my_list = [x/10 for x in arr]
# # print(my_list)