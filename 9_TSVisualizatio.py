import numpy as np
import matplotlib.pyplot as plt
import datetime as dtime
import matplotlib as mat
from matplotlib import font_manager

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

    return pointNumLngLatMap,pointsDic

# 可视化时间序列，并计算NDHDNTL
def visTimeSeries(pointsDic, city):
    # 处理未校正数据
    pointsDic_less10 = {}
    for key in pointsDic:
        pointsDic_less10[key] = []
        for item in pointsDic[key]:
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

    # 绘制曲线
    count = 0
    for key in pointsDic_less10:
        if (count > 20):
            break
        # # Normalized Difference between Hotspot and Darkspot NTL radiance (NDHDNTL):
        # ori_min = np.min(visNTL_dic[key])
        # ori_max = np.max(visNTL_dic[key])
        # print(key,"original NTL NDHDNTL value : ", (ori_max - ori_min) / (ori_max + ori_min))
        #
        # # CV 消除平均数不同对两个或多个资料变异程度比较的影响（这里可以消除居住区和商业区等因为用地类型不同，而造成均值不同的情况）
        # ori_cv_score = np.std(visNTL_dic[key]) / np.mean(visNTL_dic[key]) * 100
        # print(key, "original NTL cv value : ", ori_cv_score)

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
        plt.plot_date(time_datetime, visNTL_dic[key], color='#0072B2', label='原始时间序列',linestyle='-',marker='.')
        # plt.plot(visTime_dic_fit[key],visNTL_dic_fit[key],color='green',label='fit(Zenith 0)')
        # plt.plot_date(time_datetime, visNTL_dic_fit[key], color='#0072B2', label='角度归一化后时间序列',linestyle='-',marker='')  # 蓝色#0072B2
        # plt.title(r"$\bf{Los\ Angeles\ " + key + "}$",{'size': 16})
        # plt.title(key, fontproperties="SimHei",fontsize=22)
        plt.title(city+ " " + key, fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=22)
        plt.xlabel(u"日期",
                   fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
                   fontsize=22)
        plt.ylabel(r"夜光辐亮度", labelpad=15,
                   fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
                   fontsize=22)
        # plt.legend(loc="lower left", prop={'size': 22, "family": "SimHei"})
        plt.yticks(fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        plt.xticks(fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        plt.tick_params(labelsize=16)
        # plt.xlabel(r"$\bf{VZA(Degree)}$",{'size': 16})
        # plt.ylabel(r"$\bf{DNB\ BRDF-Corrected\ NTL\ Radiance}$",{'size': 16})
        # plt.legend(prop={'size': 16})
        dataFormat = mat.dates.DateFormatter('%Y-%m-%d')
        plt.gca().xaxis.set_major_formatter(dataFormat)
        # plt.xticks(rotation=320)
        # plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))   #更改横坐标的密度
        test_time = ["20230206", "20230220"]
        for ii in range(len(test_time)):
            datetime_temp = dtime.datetime.strptime(test_time[ii], "%Y%m%d")
            test_time[ii] = (datetime_temp)
        for x_value in test_time:
            plt.axvline(x=x_value, color='lightgrey', linewidth=3, linestyle='--')
        # plt.grid(b="True",axis="x")
        plt.grid(b="True", axis="y")
        plt.show()
        count += 1

if __name__=="__main__":
    # 需要读取的文件夹路径
    Event_ID = "SYR_20220101_20230301"
    # city_list = ["Adiyaman",
    #               "Aleppo",
    #               "Antakya",
    #               "Gaziantep",
    #               "Kahramanmaras",
    #               "Kirikhan",
    #               "Latakia",
    #               "Samandag"]
    city_list = ["Adiyaman",
                 "Kirikhan",
                 "Samandag",
                 "Antakya"]
    for city in city_list:
        work_dic = "G:\\postgraduate\\postgraduate_bishe\\TS_Txt_Constrained_By_LC_Larger50%_3_3\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_" + city
        # work_dic = "G:\\postgraduate\\postgraduate_bishe\\TS_Txt_Constrained_By_LC_Larger50%_3_3\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_" + city
        # work_dic = "G:\\postgraduate\\postgraduate_bishe\\TS_Txt_Constrained_By_LC_Larger50%_3_3\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_" + city + "_more50_wholeSeries_Prophet"
        # 读取经过筛选的有效数据（保存在文件中）
        pointNumLngLatMap, pointsDic = readFile(work_dic)

        # 可视化时间序列，并计算NDHDNTL
        visTimeSeries(pointsDic, city)
