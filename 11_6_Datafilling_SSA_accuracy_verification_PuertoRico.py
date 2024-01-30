from datetime import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import math

from matplotlib import font_manager
from dataloader_with_time import loadData
import datetime as dtime

from mssa.mssa import mSSA

def d_to_jd(time):
    fmt = '%Y.%m.%d'
    dt = datetime.strptime(time, fmt)
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday

def jd_to_time(time):
    dt = datetime.strptime(time, '%Y%j').date()
    fmt = '%Y.%m.%d'
    return dt.strftime(fmt)

def mean_forecast_err(train_df,testIndex_list,df_dsAndyhat):
    mean_value = 0
    count = 0
    for tsIndex in testIndex_list:
        yhat = df_dsAndyhat.loc[tsIndex, 'yhat']
        y = train_df.loc[tsIndex,'y']
        mean_value += math.fabs(y-yhat)
    mean_value = mean_value / len(testIndex_list)
    return mean_value

def mean_forecast_err1(test_NTLValue_series,testIndex_list,df_dsAndyhat):
    mean_value = 0
    count_index = 0
    for tsIndex in testIndex_list:
        yhat = df_dsAndyhat[tsIndex]
        y = test_NTLValue_series[count_index]
        count_index += 1
        mean_value += math.fabs(y-yhat)
    mean_value = mean_value / len(testIndex_list)
    return mean_value

def fit_SSA(time_series, NTLValue_series, alldataIndex, trainingIndex, validationIndex, key):
    for i in range(len(time_series)):
        time_series[i] = str(time_series[i])

    NTLValue_series_new = []
    validation_NTLValues = []
    allData_NTLValue = []
    for i in range(len(time_series)):
        if (i in validationIndex):
            validation_NTLValues.append(NTLValue_series[i])
            NTLValue_series_new.append(np.nan)
        elif (NTLValue_series[i] >= 65535):
            NTLValue_series_new.append(np.nan)
        elif (i in alldataIndex):
            NTLValue_series_new.append(NTLValue_series[i])
            allData_NTLValue.append(NTLValue_series[i])

    pred = fill_value(NTLValue_series_new)

    mape = mean_forecast_err1(validation_NTLValues, validationIndex, pred)
    print("mape:", mape)
    relative_error_once = mape / np.mean(allData_NTLValue)
    print("relative error:", relative_error_once)
    return relative_error_once

def getDatafillingTS(df, forecast):
    datafilling_TS = []
    for i in range(len(forecast)):
        if (np.isnan(df[i])):
            datafilling_TS.append(forecast[i])
        else:
            datafilling_TS.append(df[i])

    # # 全部用拟合结果
    # for i in range(len(forecast)):
    #     datafilling_TS.append(forecast[i])

    return datafilling_TS

def fit_SSA_getTS(time_series, NTLValue_series, alldataIndex, key, flag, pic_save_dir):
    # 重新组织时间数据
    time_datetime = []

    for i in range(len(time_series)):
        time_series[i] = str(time_series[i])

        datetime_temp = dtime.datetime.strptime(time_series[i], "%Y%m%d")
        time_datetime.append(datetime_temp)

    NTLValue_series_new = [np.nan if i >= 65535.0 else i for i in NTLValue_series]
    pred = fill_value(NTLValue_series_new)

    training_NTLValues = []
    for i in alldataIndex:
        training_NTLValues.append(NTLValue_series_new[i])

    mape = mean_forecast_err1(training_NTLValues, alldataIndex, pred)
    print("mape:", mape)

    relative_error_once = mape / np.mean(training_NTLValues)
    print("relative error:", relative_error_once)

    datafilling_TS = getDatafillingTS(NTLValue_series_new, pred)

    if (flag):
        mask = np.isnan(NTLValue_series_new)

        plt.plot_date(time_datetime, NTLValue_series_new, color="red", label="原始的夜光数据", linewidth=3,linestyle='-', marker='')
        plt.plot_date(time_datetime, pred, color="blue", label="拟合并补值的夜光数据", linewidth=3, linestyle='-',marker='')
        filledTimes = []
        filledValues = []
        for k in range(len(mask)):
            if (mask[k]):
                filledTimes.append(time_datetime[k])
                filledValues.append(pred[k])
        plt.scatter(filledTimes, filledValues, c='g', s=30)
        plt.legend(loc='lower left', prop={'size': 15, "family": "SimHei"})
        plt.xlabel(u"日期", {'size': 16},
                   fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf"), fontsize=22)
        plt.ylabel(u"夜光辐亮度", {'size': 16},
                   fontproperties=font_manager.FontProperties(fname="C:/Windows/Fonts/simhei.ttf"), fontsize=22)
        plt.yticks(fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        plt.xticks(fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        plt.tick_params(labelsize=20)
        plt.savefig(pic_save_dir + "\\" + key + ".png", bbox_inches='tight')

    return [datafilling_TS, key]

def writeDatafillingResult(f,res,time_list):
    f.write("pointNum:YYYYMMDD,NTLValue;..." + "\n")
    for i in range(len(res)):
        lizt = res[i]
        ntl_list = lizt[0]
        keyword = lizt[1]
        lines = keyword + ":"
        for j in range(len(ntl_list)):
            if (j == 0):
                lines += (str(time_list[j])+","+str(ntl_list[j]))
            else:
                lines += (";"+str(time_list[j]) + "," + str(ntl_list[j]))
        lines += "\n"
        f.write(lines)
        f.flush()

def writeAccuracyResult(f,res,key_list):
    f.write("pointNum:error value" + "\n")
    for i in range(len(res)):
        error_value = res[i]
        keyword = key_list[i]
        lines = keyword + ":" + str(error_value) + "\n"
        f.write(lines)
        f.flush()
    mean_error = np.mean(res)
    f.write("mean_error:" + str(mean_error) + "\n")
    f.flush()

def fill_value(data):
    def _fill_value(data):
        df = pd.DataFrame(data=data, columns=['data'])
        model = mSSA(rank=None, fill_in_missing = True)
        model.update_model(df)

        df2 = model.predict('data', 0, df.shape[0]-1)
        pred = df2.loc[:, 'Mean Predictions'].values

        return pred

    pred = _fill_value(data)
    while True:
        mask = np.isnan(pred)
        if np.any(mask):
            pred2 = _fill_value(pred)
            pred[mask] = pred2[mask]
        else:
            break
    return pred

# 奇异谱分析（SSA）插值方法
# 在时间序列分析中，「奇异谱分析」（「SSA」）是一种非参数谱估计方法
# SSA 可以帮助分解时间序列分解为组件的总和，每个组件都有有意义的解释。如下图所示，奇异谱分析分解出来了趋势、变化和噪声三部分。
# SSA只考虑数据本身的特征，不考虑其他因素，特别适合于插补、平稳时间序列的预测
def test_SSA():
    x = np.arange(365)
    y = np.sin(x * np.pi * 2 / 365) + np.random.randn(x.size) * 0.2

    y[:5] = np.nan
    y[-30:] = np.nan
    y[90:95] = np.nan
    y[200:205] = np.nan
    y[300:305] = np.nan

    pred = fill_value(y)
    mask = np.isnan(y)

    plt.plot(x, y)
    plt.plot(x, pred)
    plt.scatter(x[mask], pred[mask], c='r', s=3)

    plt.show()

if __name__=="__main__":
    # test_SSA()
    name_list = ["Arecibo",
                 "Bayamon",
                 "Caguas",
                 "Carolina",
                 "Guayama",
                 "Humacao",
                 "Ponce",
                 "SanJuan"]
    parent_dir = "D:\\VZA_Article\\data\\event_longTime\\id18_20180121_20190120\\"
    # time_series_type = "new_method"
    time_series_type = "TS_Txt"

    start_time = "20180121"
    end_time = "20190120"

    for name in name_list:
        file_path = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_"+str(name)
        '''
         time_list - YYYYMMDD
         normalized_ntl_list - float value
         allData_Index - data index
         all_crossValidation_trianingData_Index - 20 length list, 95% data
         all_crossValidation_validationData_Index - 20 length list, 5% data
         key_list - key
        '''
        pic_save_dir = parent_dir + time_series_type

        datasets = loadData(file_path, start_time, end_time)

        # 进行补值精度验证
        accuracy_list = []
        for i in range(len(datasets)):
            key_list = datasets[i][-1]
            eachPixel = datasets[i]

            cross_validation_count = len(eachPixel[3])
            # 每个像素的补值精度（交叉验证次数）
            results = []
            for j in range(cross_validation_count):
                result = fit_SSA(eachPixel[0], eachPixel[1], eachPixel[2], eachPixel[3][j], eachPixel[4][j], key_list[i])
                results.append(result)

            average_error = np.mean(results)
            accuracy_list.append(average_error)

        # 结果写入文件
        outputFile = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_" + str(name) + "_more50_SSA_accuracy_error_afterfit"
        f = open(outputFile, 'w')
        key_list = []
        if (len(datasets)):
            key_list = datasets[0][-1]
        writeAccuracyResult(f, accuracy_list, key_list)
        print('finished：', outputFile)
        f.close()
