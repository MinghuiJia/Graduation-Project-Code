import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import datetime as dtime
import matplotlib as mat
from datetime import datetime
import matplotlib.ticker as ticker

def d_to_jd(time):
    fmt = '%Y.%m.%d'
    dt = datetime.strptime(time, fmt)
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday

def jd_to_time(time):
    dt = datetime.strptime(time, '%Y%j').date()
    fmt = '%Y.%m.%d'
    return dt.strftime(fmt)

def processPixelTimeSeries(time_list, ntl_list, start_time, end_time):
    new_ntl_list = []
    new_time_list = []

    start_time_day = str(d_to_jd(start_time[:4] + "." + start_time[4:6] + "." +start_time[6:]))[4:]
    end_time_day = str(d_to_jd(end_time[:4] + "." + end_time[4:6] + "." +end_time[6:]))[4:]

    i_count = 0
    list_index = 0  # 用于记录添加到列表时的索引

    # 先判断第一天
    firstTime = time_list[0]
    current_time = d_to_jd(firstTime[:4] + "." + firstTime[4:6] + "." +firstTime[6:])
    # 如果第一天不是20221/1时，需要把前面的数据也补上(不同数据需要区别对待)
    if (str(current_time)[-3:] != start_time_day):
        before_time = str(current_time)[:-3] + start_time_day
        before_time = int(before_time)
        diff_count = current_time - before_time
        for j in range(diff_count):
            YYYYMMDD_list = jd_to_time(str(before_time + j)).split('.')
            new_time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
            new_ntl_list.append(float(np.nan))
            list_index += 1

    for i in range(len(time_list)-1):
        i_count = i
        time = time_list[i]
        ntl = ntl_list[i]

        time_next = time_list[i+1]
        ntl_next = ntl_list[i+1]

        last_time = d_to_jd(time_next[:4] + "." + time_next[4:6] + "." + time_next[6:])
        pre_time = d_to_jd(time[:4] + "." + time[4:6] + "." + time[6:])
        diff_count = int(last_time) - int(pre_time)

        if (diff_count > 1 and diff_count < 365):
            new_time_list.append(int(time))
            new_ntl_list.append(float(ntl))
            list_index += 1

            for j in range(1, diff_count):
                YYYYMMDD_list = jd_to_time(str(int(pre_time) + j)).split('.')
                new_time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
                new_ntl_list.append(float(np.nan))
                list_index += 1
        # 存在跨年的问题
        elif (diff_count > 365):
            # 先把这一天添加进去
            new_time_list.append(int(time))
            new_ntl_list.append(float(ntl))
            list_index += 1

            year_temp = int(str(pre_time)[0:4])
            day_temp = int(str(pre_time)[4:])
            if (year_temp % 4 == 0):
                if (day_temp < 366):
                    for i in range(366 - day_temp):
                        YYYYMMDD_list = jd_to_time(str(int(pre_time) + i + 1)).split('.')
                        new_time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
                        new_ntl_list.append(float(np.nan))
                        list_index += 1
            else:
                if (day_temp < 365):
                    for i in range(365 - day_temp):
                        YYYYMMDD_list = jd_to_time(str(int(pre_time) + i + 1)).split('.')
                        new_time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
                        new_ntl_list.append(float(np.nan))
                        list_index += 1

            # 上一年补全之后，下一年不是从1开始
            if (str(last_time)[-3:] != "001"):
                before_time = str(last_time)[:-3] + "001"
                before_time = int(before_time)
                diff_count = last_time - before_time
                for j in range(diff_count):
                    YYYYMMDD_list = jd_to_time(str(before_time + j)).split('.')
                    new_time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
                    new_ntl_list.append(float(np.nan))
                    list_index += 1
        else:
            new_time_list.append(int(time))
            new_ntl_list.append(float(ntl))
            list_index += 1


    time_last = time_list[i_count + 1]
    ntl_last = ntl_list[i_count + 1]
    new_time_list.append(int(time_last))
    new_ntl_list.append(float(ntl_last))
    list_index += 1
    end_time = d_to_jd(time_last[:4] + "." + time_last[4:6] + "." + time_last[6:])
    year = int(str(end_time)[0:4])
    day = int(str(end_time)[4:])

    # 如果最后一天不是20235/1时，需要把后面的数据也补上(不同数据需要区别对待)
    if (str(end_time)[-3:] != end_time_day):
        after_time = str(end_time)[:-3] + end_time_day
        after_time = int(after_time)
        before_time = int(end_time)
        diff_count = after_time - before_time
        for j in range(diff_count):
            YYYYMMDD_list = jd_to_time(str(before_time + j + 1)).split('.')
            new_time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
            new_ntl_list.append(float(65535))
            list_index += 1

    return new_time_list, new_ntl_list

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

def readFileAfterDataFilling(filePath):
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
                pointsDic[pointNum].append([float(value_list[1]),65535,value_list[0]])

    return pointsDic

# 可视化时间序列，并计算NDHDNTL
def visTimeSeries(pointsDic,pointsDic_fit, area, show_point_key, start_time, end_time):
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
        if (key == show_point_key):

            time_list = visTime_dic[key]
            ntl_list = visNTL_dic[key]
            ntl_fit_list = visNTL_dic_fit[key]
            new_time_list, new_ntl_list = processPixelTimeSeries(time_list, ntl_list, start_time, end_time)
            new_time_fit_list, new_ntl_fit_list = processPixelTimeSeries(time_list, ntl_fit_list, start_time, end_time)

            # 重新组织时间数据
            time_datetime = []
            for i in range(len(new_time_list)):
                datetime_temp = dtime.datetime.strptime(str(new_time_list[i]), "%Y%m%d")
                time_datetime.append(datetime_temp)

            # plt.tick_params
            plt.figure(figsize=(8, 6))
            # plt.tick_params(labelsize=16)

            # plt.plot(visTime_dic[key], visNTL_dic[key], color='red',label='original')
            # plt.plot_date(time_datetime, visNTL_dic[key], color='red', label='原始时间序列',linestyle='-',marker='')
            plt.plot_date(time_datetime, new_ntl_list, color='red', label='original time series', linestyle='-', linewidth=3, marker='')
            # plt.plot(visTime_dic_fit[key],visNTL_dic_fit[key],color='green',label='fit(Zenith 0)')
            # plt.plot_date(time_datetime, visNTL_dic_fit[key], color='#0072B2', label='角度归一化后时间序列',linestyle='-',marker='')  # 蓝色#0072B2
            plt.plot_date(time_datetime, new_ntl_fit_list, color='#0072B2', label='angle-normalized time series', linestyle='-', linewidth=3, marker='')  # 蓝色#0072B2
            # plt.title(r"$\bf{Los\ Angeles\ " + key + "}$",{'size': 16})
            # plt.title(area+r" point "+key, fontproperties="SimHei",fontsize=22)
            plt.title(area + r" " + key, fontproperties="Adobe Gothic Std", fontsize=22)
            # plt.xlabel(u"日期",
            #            fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
            #            fontsize=22)
            plt.xlabel(u"Date",
                       fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf", weight='extra bold'),
                       fontsize=22)
            plt.ylabel(r"夜光辐亮度", labelpad=15,
                       fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
                       fontsize=22)
            # plt.ylabel(r"Nighttime Light Radiance", labelpad=15,
            #            fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf", weight='extra bold'),
            #            fontsize=22)
            # plt.legend(loc="lower right", prop={'size': 22, "family": "SimHei"})
            # plt.legend(loc="upper left", prop={'size': 18, "family": "Adobe Gothic Std"})
            plt.yticks(fontproperties=font_manager.FontProperties(
                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
            plt.xticks(fontproperties=font_manager.FontProperties(
                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
            plt.tick_params(labelsize=16)
            # plt.xlabel(r"$\bf{VZA(Degree)}$",{'size': 16})
            # plt.ylabel(r"$\bf{DNB\ BRDF-Corrected\ NTL\ Radiance}$",{'size': 16})
            # plt.legend(prop={'size': 16})
            dataFormat = mat.dates.DateFormatter('%Y-%m')
            plt.gca().xaxis.set_major_formatter(dataFormat)
            # plt.xticks(rotation=320)
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(30))   #更改横坐标的密度

            plt.show()

def visVZATimeSeries(pointsDic,pointsDic_fit, area, show_point_key, start_time, end_time):
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
    visVZA_dic = {}
    for key in pointsDic_less10:
        NTL_value = []
        time_value = []
        vza_value = []
        for i in range(len(pointsDic_less10[key])):
            NTL_value.append(pointsDic_less10[key][i][0])
            time_value.append(str(pointsDic_less10[key][i][2]))
            vza_value.append(pointsDic_less10[key][i][1])
        visNTL_dic[key] = NTL_value
        visTime_dic[key] = time_value
        visVZA_dic[key] = vza_value

    # 绘制曲线
    for key in pointsDic_less10:
        if (key == show_point_key):

            time_list = visTime_dic[key]
            ntl_list = visNTL_dic[key]
            vza_list = visVZA_dic[key]
            new_time_list, new_ntl_list = processPixelTimeSeries(time_list, ntl_list, start_time, end_time)
            new_time_vza_list, new_vza_list = processPixelTimeSeries(time_list, vza_list, start_time, end_time)

            # 重新组织时间数据
            time_datetime = []
            for i in range(len(new_time_list)):
                datetime_temp = dtime.datetime.strptime(str(new_time_list[i]), "%Y%m%d")
                time_datetime.append(datetime_temp)

            # plt.tick_params
            plt.figure(figsize=(8, 6))
            # plt.tick_params(labelsize=16)

            # plt.plot(visTime_dic[key], visNTL_dic[key], color='red',label='original')
            # plt.plot_date(time_datetime, visNTL_dic[key], color='red', label='原始时间序列',linestyle='-',marker='')

            # plt.plot(visTime_dic_fit[key],visNTL_dic_fit[key],color='green',label='fit(Zenith 0)')
            # plt.plot_date(time_datetime, visNTL_dic_fit[key], color='#0072B2', label='角度归一化后时间序列',linestyle='-',marker='')  # 蓝色#0072B2

            # plt.title(r"$\bf{Los\ Angeles\ " + key + "}$",{'size': 16})
            # plt.title(area+r" point "+key, fontproperties="SimHei",fontsize=22)
            # plt.xlabel(u"日期",
            #            fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
            #            fontsize=22)
            plt.ylabel(r"夜光辐亮度", labelpad=15,
                       fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
                       fontsize=22)
            # plt.legend(loc="lower right", prop={'size': 22, "family": "SimHei"})
            # plt.legend(loc="upper left", prop={'size': 18, "family": "Adobe Gothic Std"})
            # plt.xlabel(r"$\bf{VZA(Degree)}$",{'size': 16})
            # plt.ylabel(r"$\bf{DNB\ BRDF-Corrected\ NTL\ Radiance}$",{'size': 16})
            # plt.legend(prop={'size': 16})

            # plt.xticks(rotation=320)
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(30))   #更改横坐标的密度

            plt.title(area + r" " + key, fontproperties="Adobe Gothic Std", fontsize=22)
            plt.xlabel(u"Date",
                       fontproperties=font_manager.FontProperties(
                           fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf",
                           weight='extra bold'),
                       fontsize=22)
            plt.yticks(fontproperties=font_manager.FontProperties(
                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
            plt.xticks(fontproperties=font_manager.FontProperties(
                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
            plt.tick_params(labelsize=16)
            dataFormat = mat.dates.DateFormatter('%Y-%m')
            plt.gca().xaxis.set_major_formatter(dataFormat)

            plt.plot_date(time_datetime, new_vza_list, color='orange', label='angle-normalized time series',
                          linestyle='-', linewidth=3, marker='')  # 蓝色#0072B2
            # plt.ylabel(r"Nighttime Light Radiance", labelpad=15,
            #            fontproperties=font_manager.FontProperties(
            #                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf",
            #                weight='extra bold'),
            #            fontsize=22)
            plt.show()
def visNTLTimeSeries(pointsDic,pointsDic_fit, area, show_point_key, start_time, end_time):
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
    visVZA_dic = {}
    for key in pointsDic_less10:
        NTL_value = []
        time_value = []
        vza_value = []
        for i in range(len(pointsDic_less10[key])):
            NTL_value.append(pointsDic_less10[key][i][0])
            time_value.append(str(pointsDic_less10[key][i][2]))
            vza_value.append(pointsDic_less10[key][i][1])
        visNTL_dic[key] = NTL_value
        visTime_dic[key] = time_value
        visVZA_dic[key] = vza_value

    # 绘制曲线
    for key in pointsDic_less10:
        if (key == show_point_key):

            time_list = visTime_dic[key]
            ntl_list = visNTL_dic[key]
            vza_list = visVZA_dic[key]
            new_time_list, new_ntl_list = processPixelTimeSeries(time_list, ntl_list, start_time, end_time)
            new_time_vza_list, new_vza_list = processPixelTimeSeries(time_list, vza_list, start_time, end_time)

            # 重新组织时间数据
            time_datetime = []
            for i in range(len(new_time_list)):
                datetime_temp = dtime.datetime.strptime(str(new_time_list[i]), "%Y%m%d")
                time_datetime.append(datetime_temp)

            # plt.tick_params
            plt.figure(figsize=(8, 6))
            # plt.tick_params(labelsize=16)

            # plt.plot(visTime_dic[key], visNTL_dic[key], color='red',label='original')
            # plt.plot_date(time_datetime, visNTL_dic[key], color='red', label='原始时间序列',linestyle='-',marker='')

            # plt.plot(visTime_dic_fit[key],visNTL_dic_fit[key],color='green',label='fit(Zenith 0)')
            # plt.plot_date(time_datetime, visNTL_dic_fit[key], color='#0072B2', label='角度归一化后时间序列',linestyle='-',marker='')  # 蓝色#0072B2

            # plt.title(r"$\bf{Los\ Angeles\ " + key + "}$",{'size': 16})
            # plt.title(area+r" point "+key, fontproperties="SimHei",fontsize=22)
            # plt.xlabel(u"日期",
            #            fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
            #            fontsize=22)
            plt.ylabel(r"夜光辐亮度", labelpad=15,
                       fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
                       fontsize=22)
            # plt.legend(loc="lower right", prop={'size': 22, "family": "SimHei"})
            # plt.legend(loc="upper left", prop={'size': 18, "family": "Adobe Gothic Std"})
            # plt.xlabel(r"$\bf{VZA(Degree)}$",{'size': 16})
            # plt.ylabel(r"$\bf{DNB\ BRDF-Corrected\ NTL\ Radiance}$",{'size': 16})
            # plt.legend(prop={'size': 16})

            # plt.xticks(rotation=320)
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(30))   #更改横坐标的密度

            plt.title(area + r" " + key, fontproperties="Adobe Gothic Std", fontsize=22)
            plt.xlabel(u"Date",
                       fontproperties=font_manager.FontProperties(
                           fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf",
                           weight='extra bold'),
                       fontsize=22)
            plt.yticks(fontproperties=font_manager.FontProperties(
                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
            plt.xticks(fontproperties=font_manager.FontProperties(
                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
            plt.tick_params(labelsize=16)
            dataFormat = mat.dates.DateFormatter('%Y-%m')
            plt.gca().xaxis.set_major_formatter(dataFormat)

            plt.plot_date(time_datetime, new_ntl_list, color='#0072B2', label='original time series', linestyle='-', linewidth=3,
                          marker='')
            # plt.ylabel(r"Nighttime Light Radiance", labelpad=15,
            #            fontproperties=font_manager.FontProperties(
            #                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf",
            #                weight='extra bold'),
            #            fontsize=22)
            plt.show()

def visDataFillingTimeSeries(pointsDic,pointsDic_fit, pointsLoc, area, show_point_key, start_time, end_time):
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

    # 处理占位数据
    pointsLoc_less10 = {}
    for key in pointsLoc:
        pointsLoc_less10[key] = []
        for item in pointsLoc[key]:
            if (item[1]):
                item_temp = [item[0], item[1], int(item[2])]
                pointsLoc_less10[key].append(item_temp)
        pointsLoc_less10[key].sort(key=lambda x: x[2])  # 指定某列排序

    visNTL_dic_loc = {}
    visTime_dic_loc = {}
    for key in pointsLoc_less10:
        NTL_value = []
        time_value = []
        for i in range(len(pointsLoc_less10[key])):
            NTL_value.append(pointsLoc_less10[key][i][0])
            time_value.append(str(pointsLoc_less10[key][i][2]))
        visNTL_dic_loc[key] = NTL_value
        visTime_dic_loc[key] = time_value

    # 绘制曲线
    for key in pointsDic_less10:
        if (key == show_point_key):

            time_list = visTime_dic[key]
            ntl_list = visNTL_dic[key]
            ntl_fit_list = visNTL_dic_fit[key]
            ntl_list_loc = visNTL_dic_loc[key]
            new_time_list, new_ntl_list = processPixelTimeSeries(time_list, ntl_list, start_time, end_time)
            new_time_list_loc, new_ntl_list_loc = processPixelTimeSeries(time_list, ntl_list_loc, start_time, end_time)

            # 重新组织时间数据
            time_datetime = []
            for i in range(len(new_time_list)):
                datetime_temp = dtime.datetime.strptime(str(new_time_list[i]), "%Y%m%d")
                time_datetime.append(datetime_temp)

            # plt.tick_params
            plt.figure(figsize=(8, 6))
            # plt.tick_params(labelsize=16)

            # plt.plot(visTime_dic[key], visNTL_dic[key], color='red',label='original')
            # plt.plot_date(time_datetime, visNTL_dic[key], color='red', label='原始时间序列',linestyle='-',marker='')

            # plt.plot(visTime_dic_fit[key],visNTL_dic_fit[key],color='green',label='fit(Zenith 0)')
            # plt.plot_date(time_datetime, visNTL_dic_fit[key], color='#0072B2', label='角度归一化后时间序列',linestyle='-',marker='')  # 蓝色#0072B2
            plt.plot_date(time_datetime, ntl_fit_list, color='#0072B2', label='angle-normalized time series', linestyle='-', linewidth=3, marker='')  # 蓝色#0072B2
            plt.plot_date(time_datetime, new_ntl_list, color='red', label='original time series', linestyle='-', linewidth=3,
                          marker='')
            # plt.plot_date(time_datetime, new_ntl_list_loc, color='black', label='original time series', linestyle='',
            #               marker='')
            # plt.title(r"$\bf{Los\ Angeles\ " + key + "}$",{'size': 16})
            # plt.title(area+r" point "+key, fontproperties="SimHei",fontsize=22)
            plt.title(area + r" " + key, fontproperties="Adobe Gothic Std", fontsize=22)
            # plt.xlabel(u"日期",
            #            fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
            #            fontsize=22)
            plt.xlabel(u"Date",
                       fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf", weight='extra bold'),
                       fontsize=22)
            plt.ylabel(r"夜光辐亮度", labelpad=15,
                       fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", weight='extra bold'),
                       fontsize=22)
            # plt.ylabel(r"Nighttime Light Radiance", labelpad=15,
            #            fontproperties=font_manager.FontProperties(fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf", weight='extra bold'),
            #            fontsize=22)
            # plt.legend(loc="lower right", prop={'size': 22, "family": "SimHei"})
            # plt.legend(loc="upper left", prop={'size': 18, "family": "Adobe Gothic Std"})
            plt.yticks(fontproperties=font_manager.FontProperties(
                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
            plt.xticks(fontproperties=font_manager.FontProperties(
                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
            plt.tick_params(labelsize=16)
            # plt.xlabel(r"$\bf{VZA(Degree)}$",{'size': 16})
            # plt.ylabel(r"$\bf{DNB\ BRDF-Corrected\ NTL\ Radiance}$",{'size': 16})
            # plt.legend(prop={'size': 16})
            dataFormat = mat.dates.DateFormatter('%Y-%m')
            plt.gca().xaxis.set_major_formatter(dataFormat)
            # plt.xticks(rotation=320)
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(30))   #更改横坐标的密度

            plt.show()


if __name__ == "__main__":
    start_time = "20180121"
    end_time = "20190120"

    # 需要读取的文件夹路径
    work_dic = "D:\\VZA_article\\data\\event_longTime\\id18_20180121_20190120\\TS_Txt_Constrained_By_LC_Larger50%\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Arecibo"
    fit_result_path = "D:\\VZA_article\\data\\event_longTime\\id18_20180121_20190120\\TS_Txt_Constrained_By_LC_Larger50%\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_Arecibo"
    datafilling_afterfit_result_path = "D:\\VZA_article\\data\\event_longTime\\id18_20180121_20190120\\TS_Txt_Constrained_By_LC_Larger50%\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Arecibo_more50_wholeSeries_Prophet_afterfit"
    # work_dic = "D:\\VZA_article\\data\\event_longTime\\id18_20180121_20190120\\TS_Txt_Constrained_By_LC_Larger50%\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_Bayamon"
    # fit_result_path = "D:\\VZA_article\\data\\event_longTime\\id18_20180121_20190120\\TS_Txt_Constrained_By_LC_Larger50%\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_Bayamon"

    # 读取经过筛选的有效数据（保存在文件中）
    pointNumLngLatMap, pointsDic = readFile(work_dic)

    # 读取筛选数据经过角度归一化后的数据（读取之前需要执行visScatterAndFitCurve进行校正）
    pointNumLngLatMap_fit, pointsDic_fit = readFile(fit_result_path)

    # 读取角度校正后补值的数据
    pointsDic_datafilling_afterfit = readFileAfterDataFilling(datafilling_afterfit_result_path)

    # 可视化缺失的数据和观测角度
    visNTLTimeSeries(pointsDic, pointsDic_fit, "Arecibo", "point 2", start_time, end_time)
    visVZATimeSeries(pointsDic, pointsDic_fit, "Arecibo", "point 2", start_time, end_time)

    # # 可视化时间序列，并计算NDHDNTL
    visTimeSeries(pointsDic, pointsDic_fit, "Arecibo", "point 2", start_time, end_time)
    # 可视化角度校正补值前后的对比图
    visDataFillingTimeSeries(pointsDic_fit, pointsDic_datafilling_afterfit, pointsDic, "Arecibo", "point 2", start_time, end_time)

    # visTimeSeries(pointsDic, pointsDic_fit, "Bayamon", "point 8", start_time, end_time)
