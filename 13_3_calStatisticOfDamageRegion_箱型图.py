import matplotlib.pyplot as plt
import gdal
import pandas as pd
import numpy as np
import csv
from matplotlib import font_manager
import datetime as dtime
import matplotlib as mat
import seaborn as sns

def read_tiff(filename):
    datasets=gdal.Open(filename)  # 读取文件
    row=datasets.RasterXSize    # 获取数据的宽
    col=datasets.RasterYSize    # 获取数据的高
    band=datasets.RasterCount   # 获取数据的波段数

    geoTransform = datasets.GetGeoTransform()   # 仿射矩阵
    proj = datasets.GetProjection()     # 获取投影信息
    data=np.zeros([col,row,band])
    for i in range(band):
        dt=datasets.GetRasterBand(i+1)  # 读取i+1波段信息（读取时从1开始）
        data[:,:,i]=dt.ReadAsArray(0,0,row,col) # Getting data from 0 rows and 0 columns
    return data,geoTransform,proj

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
    sns.distplot(nums, bins=range(0,100,2), hist=is_hist, kde=is_kde, rug=is_rug,
                 hist_kws={"color": "steelblue"}, kde_kws={"color": "purple"},
                 vertical=is_vertical, norm_hist=is_norm_hist, label="Bayamon Pre")
    # sns.distplot(nums2, bins=range(0,100,3), hist=is_hist, kde=is_kde, rug=is_rug,
    #              hist_kws={"color": "steelblue"}, kde_kws={"color": "purple"},
    #              vertical=is_vertical, norm_hist=is_norm_hist, label="SanJuan")

    sns.distplot(nums2, bins=range(0, 100, 2), hist=is_hist, kde=is_kde, rug=is_rug,
                 hist_kws={"color": "red"}, kde_kws={"color": "red"},
                 vertical=is_vertical, norm_hist=is_norm_hist, label="Bayamon Post")

    # plt.xlim(0, 100)
    plt.xlim(0, 60)
    # 添加标题
    # plt.title("Distribution")
    # 添加x轴和y轴标签
    plt.legend(loc='upper right', prop={'size': 14, "family": "Adobe Gothic Std"})
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

def draw_boxplot(num1, num2, num3, num4, num5, num6,
                 num7, num8, num9, num10, num11, num12,
                 num13, num14, num15):
    num1 = np.array(num1)
    num2 = np.array(num2)
    num3 = np.array(num3)

    num4 = np.array(num4)
    num5 = np.array(num5)
    num6 = np.array(num6)

    num7 = np.array(num7)
    num8 = np.array(num8)
    num9 = np.array(num9)

    num10 = np.array(num10)
    num11 = np.array(num11)
    num12 = np.array(num12)

    num13 = np.array(num13)
    num14 = np.array(num14)
    num15 = np.array(num15)

    df1 = pd.DataFrame(num1, columns=['delta'])
    df1['time'] = 'pre'
    df1['city'] = 'Adiyaman'
    df2 = pd.DataFrame(num2, columns=['delta'])
    df2['time'] = 'post1'
    df2['city'] = 'Adiyaman'
    df3 = pd.DataFrame(num3, columns=['delta'])
    df3['time'] = 'post2'
    df3['city'] = 'Adiyaman'
    df4 = pd.DataFrame(num4, columns=['delta'])
    df4['time'] = 'pre'
    df4['city'] = 'Antakya'
    df5 = pd.DataFrame(num5, columns=['delta'])
    df5['time'] = 'post1'
    df5['city'] = 'Antakya'
    df6 = pd.DataFrame(num6, columns=['delta'])
    df6['time'] = 'post2'
    df6['city'] = 'Antakya'

    df7 = pd.DataFrame(num7, columns=['delta'])
    df7['time'] = 'pre'
    df7['city'] = 'Kahramanmaras'
    df8 = pd.DataFrame(num8, columns=['delta'])
    df8['time'] = 'post1'
    df8['city'] = 'Kahramanmaras'
    df9 = pd.DataFrame(num9, columns=['delta'])
    df9['time'] = 'post2'
    df9['city'] = 'Kahramanmaras'

    df10 = pd.DataFrame(num10, columns=['delta'])
    df10['time'] = 'pre'
    df10['city'] = 'Kirikhan'
    df11 = pd.DataFrame(num11, columns=['delta'])
    df11['time'] = 'post1'
    df11['city'] = 'Kirikhan'
    df12 = pd.DataFrame(num12, columns=['delta'])
    df12['time'] = 'post2'
    df12['city'] = 'Kirikhan'

    df13 = pd.DataFrame(num13, columns=['delta'])
    df13['time'] = 'pre'
    df13['city'] = 'Samandag'
    df14 = pd.DataFrame(num14, columns=['delta'])
    df14['time'] = 'post1'
    df14['city'] = 'Samandag'
    df15 = pd.DataFrame(num15, columns=['delta'])
    df15['time'] = 'post2'
    df15['city'] = 'Samandag'

    df = pd.concat([df1, df2, df3, df4, df5, df6,
                    df7, df8, df9, df10, df11, df12,
                    df13, df14, df15], axis=0)

    sns.set()
    ax = sns.boxplot(x="city", y="delta", data=df, hue="time", fliersize=0, width=0.7)
    # plt.xlabel(u"city", {'size': 10},
    #            fontproperties=font_manager.FontProperties(
    #                fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=18)
    plt.ylabel(u"Radiance", {'size': 10},
               fontproperties=font_manager.FontProperties(
                   fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"), fontsize=18)
    plt.yticks(fontproperties=font_manager.FontProperties(
        fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
    plt.xticks(fontproperties=font_manager.FontProperties(
        fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
    plt.ylim(0, 120)
    # plt.xlabel('alpha limit')
    # plt.ylabel('delta theta')
    # plt.legend(loc='upper left', prop={'size': 12, "family": "Adobe Gothic Std"})
    sns.move_legend(ax, bbox_to_anchor=(-0.05, -0.95), loc='upper left')
    plt.show()

# 三个时期的对比结果 灾前1个月 灾后10天 灾后1个月
if __name__=="__main__":
    work_dir = "G:\\postgraduate\\postgraduate_bishe\\VNP46A2_tif\\pre_and_post_disaster_mean_NTL_Img\\"
    country_list = ["Adiyaman", "Antakya", "Kahramanmaras", "Kirikhan", "Samandag"]

    # 里面存储每个国家的3中数据
    res = []
    # 灾前1个月数据
    temp_pre_list = []
    for city in country_list:
        dataFile = work_dir + city + "_pre_10days_disaster_Img.tif"
        data_DNB, geoTransform_DNB, proj_DNB = read_tiff(dataFile)
        data_DNB_2dim = data_DNB[:, :, 0]
        data_DNB_1dim = data_DNB_2dim.flatten()
        data_DNB_without_nan = data_DNB_1dim[~np.isnan(data_DNB_1dim)]
        temp_pre_list.append(data_DNB_without_nan/10.0)

    temp_post10day_list = []
    for city in country_list:
        dataFile = work_dir + city + "_post_10days_disaster_Img.tif"
        data_DNB, geoTransform_DNB, proj_DNB = read_tiff(dataFile)
        data_DNB_2dim = data_DNB[:, :, 0]
        data_DNB_1dim = data_DNB_2dim.flatten()
        data_DNB_without_nan = data_DNB_1dim[~np.isnan(data_DNB_1dim)]
        temp_post10day_list.append(data_DNB_without_nan/10.0)

    temp_post1month_list = []
    for city in country_list:
        dataFile = work_dir + city + "_post_1month_disaster_Img.tif"
        data_DNB, geoTransform_DNB, proj_DNB = read_tiff(dataFile)
        data_DNB_2dim = data_DNB[:, :, 0]
        data_DNB_1dim = data_DNB_2dim.flatten()
        data_DNB_without_nan = data_DNB_1dim[~np.isnan(data_DNB_1dim)]
        temp_post1month_list.append(data_DNB_without_nan/10.0)


    a = 10

    draw_boxplot(
        temp_pre_list[0], temp_post10day_list[0], temp_post1month_list[0],
        temp_pre_list[1], temp_post10day_list[1], temp_post1month_list[1],
        temp_pre_list[2], temp_post10day_list[2], temp_post1month_list[2],
        temp_pre_list[3], temp_post10day_list[3], temp_post1month_list[3],
        temp_pre_list[4], temp_post10day_list[4], temp_post1month_list[4],
    )