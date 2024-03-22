from datetime import datetime
import numpy as np
import pandas as pd
from fbprophet import Prophet
import matplotlib.pyplot as plt
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics
from fbprophet.plot import plot_cross_validation_metric
from pandas.plotting import register_matplotlib_converters
import math
import random
import copy
from pylab import mpl
import time
from matplotlib import font_manager
from dataloader_with_time import loadData

import os
import time
import multiprocessing
from joblib import Parallel, delayed

def d_to_jd(time):
    fmt = '%Y.%m.%d'
    dt = datetime.strptime(time, fmt)
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday

def jd_to_time(time):
    dt = datetime.strptime(time, '%Y%j').date()
    fmt = '%Y.%m.%d'
    return dt.strftime(fmt)

class PSO(object):
    def __init__(self, particle_num, particle_dim, iter_num, c1, c2, w, max_value, min_value, df, fdays, testIndex_list_allDst):
        self.particle_num = particle_num
        self.particle_dim = particle_dim
        self.iter_num = iter_num
        self.c1 = c1
        self.c2 = c2
        self.w = w
        self.max_value = max_value
        self.min_value = min_value
        self.df = df
        self.fdays = fdays
        self.testIndex_list_allDst = testIndex_list_allDst

    def swarm_origin(self):
        particle_loc = []
        particle_dir = []
        for i in range(self.particle_num):
            tmp1 = []
            tmp2 = []
            for j in range(self.particle_dim):
                a = random.random()
                b = random.random()
                tmp1.append(a * (self.max_value - self.min_value) + self.min_value)
                tmp2.append(b)
            particle_loc.append(tmp1)
            particle_dir.append(tmp2)

        return particle_loc, particle_dir

    def fitness(self, particle_loc):
        fitness_value = []
        for i in range(self.particle_num):
            error_value = find_params(self.df,self.fdays,self.testIndex_list_allDst,particle_loc[i][0],particle_loc[i][1],particle_loc[i][2])
            # rbf_svm = svm.SVC(kernel='rbf', C=particle_loc[i][0], gamma=particle_loc[i][1])
            # cv_scores = cross_validation.cross_val_score(rbf_svm, trainX, trainY, cv=3, scoring='accuracy')
            fitness_value.append(error_value)
        current_fitness = 99999999.0
        current_parameter = []
        for i in range(self.particle_num):
            if current_fitness > fitness_value[i]:
                current_fitness = fitness_value[i]
                current_parameter = particle_loc[i]

        return fitness_value, current_fitness, current_parameter

    def updata(self, particle_loc, particle_dir, gbest_parameter, pbest_parameters):
        for i in range(self.particle_num):
            a1 = [x * self.w for x in particle_dir[i]]
            a2 = [y * self.c1 * random.random() for y in
                  list(np.array(pbest_parameters[i]) - np.array(particle_loc[i]))]
            a3 = [z * self.c2 * random.random() for z in list(np.array(gbest_parameter) - np.array(particle_dir[i]))]
            particle_dir[i] = list(np.array(a1) + np.array(a2) + np.array(a3))
            #            particle_dir[i] = self.w * particle_dir[i] + self.c1 * random.random() * (pbest_parameters[i] - particle_loc[i]) + self.c2 * random.random() * (gbest_parameter - particle_dir[i])
            particle_loc[i] = list(np.array(particle_loc[i]) + np.array(particle_dir[i]))

        parameter_list = []
        for i in range(self.particle_dim):
            tmp1 = []
            for j in range(self.particle_num):
                tmp1.append(particle_loc[j][i])
            parameter_list.append(tmp1)
        value = []
        for i in range(self.particle_dim):
            tmp2 = []
            tmp2.append(max(parameter_list[i]))
            tmp2.append(min(parameter_list[i]))
            value.append(tmp2)

        for i in range(self.particle_num):
            for j in range(self.particle_dim):
                particle_loc[i][j] = (particle_loc[i][j] - value[j][1]) / (value[j][0] - value[j][1]) * (
                            self.max_value - self.min_value) + self.min_value

        return particle_loc, particle_dir

    def plot(self, results):
        X = []
        Y = []
        for i in range(self.iter_num):
            X.append(i + 1)
            Y.append(results[i])
        plt.plot(X, Y)
        plt.xlabel('Number of iteration', size=15)
        plt.ylabel('Value of Error', size=15)
        plt.title('PSO parameter optimization')
        plt.show()

    def main(self):
        results = []
        best_fitness = 99999999.0
        particle_loc, particle_dir = self.swarm_origin()
        gbest_parameter = []
        for i in range(self.particle_dim):
            gbest_parameter.append(0.0)
        pbest_parameters = []
        for i in range(self.particle_num):
            tmp1 = []
            for j in range(self.particle_dim):
                tmp1.append(0.0)
            pbest_parameters.append(tmp1)
        fitness_value = []
        for i in range(self.particle_num):
            fitness_value.append(99999999.0)

        for i in range(self.iter_num):
            current_fitness_value, current_best_fitness, current_best_parameter = self.fitness(particle_loc)
            for j in range(self.particle_num):
                if current_fitness_value[j] < fitness_value[j]:
                    pbest_parameters[j] = particle_loc[j]
            if current_best_fitness < best_fitness:
                best_fitness = current_best_fitness
                gbest_parameter = current_best_parameter

            print('iteration is :', i + 1, ';Best parameters:', gbest_parameter, ';loss:', best_fitness)
            results.append(best_fitness)
            fitness_value = current_fitness_value
            particle_loc, particle_dir = self.updata(particle_loc, particle_dir, gbest_parameter, pbest_parameters)
        print('Final parameters are :', gbest_parameter)
        return gbest_parameter

def find_params(df,fdays,testIndex_list,sp_scale,cp_scale,nPoints):
    params = {
        "seasonality_mode": "additive",
        "seasonality_prior_scale": sp_scale,
        "changepoint_prior_scale": cp_scale,
        "n_changepoints": nPoints,
        "daily_seasonality": False,
        "weekly_seasonality": False,
        "changepoint_range": 1
    }
    avg_err = predict_one(df, fdays, testIndex_list, params)
    return avg_err

def predict_one(train_df,fdays,testIndex_list,params):
    m = Prophet(**params)
    m.fit(train_df)
    future = m.make_future_dataframe(periods=fdays)
    forecast = m.predict(future)
    return mean_forecast_err(train_df,testIndex_list,forecast[['ds','yhat']])

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
        yhat = df_dsAndyhat.loc[tsIndex, 'yhat']
        y = test_NTLValue_series[count_index]
        count_index += 1
        mean_value += math.fabs(y-yhat)
    mean_value = mean_value / len(testIndex_list)
    return mean_value

def fit_prophet(time_series, NTLValue_series, alldataIndex, trainingIndex, validationIndex, PSO_Params):
    column_name = ['ds', 'y']
    df = pd.DataFrame(np.vstack((time_series, NTLValue_series)).T, columns=column_name)

    validation_NTLValues = []
    allData_NTLValue = []
    for i in range(len(time_series)):
        if (i in validationIndex):
            df.loc[i, 'y'] = None
            validation_NTLValues.append(NTLValue_series[i])
        elif (df.loc[i, 'y'] >= 65535):
            df.loc[i, 'y'] = None
        elif (i in alldataIndex):
            allData_NTLValue.append(NTLValue_series[i])

    particle_num = 5
    particle_dim = 3
    iter_num = 5
    c1 = 2
    c2 = 2
    w = 0.5
    max_value = int(len(alldataIndex) * 0.6)
    min_value = 0.01
    fdays = 0

    if (len(PSO_Params) != 0):
        particle_num = int(PSO_Params[0])
        iter_num = int(PSO_Params[1])
        min_value = float(PSO_Params[2])
        c1 = float(PSO_Params[3])
        c2 = float(PSO_Params[4])
        w = float(PSO_Params[5])
    print("Final PSO_Num: ", particle_num)
    print("Final PSO_Dim: ", particle_dim)
    print("Final PSO_IterNum: ", iter_num)
    print("Final PSO_Max: ", max_value)
    print("Final PSO_Min: ", min_value)
    print("Final PSO_LocalLR: ", c1)
    print("Final PSO_GlobalLR: ", c2)
    print("Final PSO_Inertial: ", w)

    pso = PSO(particle_num, particle_dim, iter_num, c1, c2, w, max_value, min_value, df, fdays, trainingIndex)
    glo_gbest_parameter = pso.main()

    m = Prophet(seasonality_mode="additive", seasonality_prior_scale=glo_gbest_parameter[0],
                changepoint_prior_scale=glo_gbest_parameter[1], n_changepoints=glo_gbest_parameter[2],
                changepoint_range=1, daily_seasonality=False, weekly_seasonality=False)

    m.fit(df)
    fday = 0
    future = m.make_future_dataframe(periods=fday, freq='D')
    forecast = m.predict(future)

    mape = mean_forecast_err1(validation_NTLValues, validationIndex, forecast[['ds', 'yhat']])
    print("mape:", mape)
    relative_error_once = mape / np.mean(allData_NTLValue)
    print("relative error:", relative_error_once)
    return relative_error_once

def getDatafillingTS(df, forecast, times):
    datafilling_TS = []
    for time in range(times):
        if (np.isnan(df.loc[time, 'y'])):
            datafilling_TS.append(forecast.loc[time,'yhat'])
        else:
            datafilling_TS.append(df.loc[time,'y'])

    # # 全部用拟合结果
    # for time in range(times):
    #     datafilling_TS.append(forecast.loc[time,'yhat'])

    return datafilling_TS
    
def fit_prophet_getTS(time_series, NTLValue_series, alldataIndex, PSO_Params, key, flag, pic_save_dir):
    for i in range(len(time_series)):
        # YYYYMMDD_list = jd_to_time(str(time_series[i])).split('.')
        # time_series[i] = str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])
        time_series[i] = str(time_series[i])

    column_name = ['ds', 'y']
    df = pd.DataFrame(np.vstack((time_series, NTLValue_series)).T, columns=column_name)
    df['y'] = df['y'].astype('float')

    training_NTLValues = []
    for i in range(len(time_series)):
        if (i in alldataIndex):
            training_NTLValues.append(NTLValue_series[i])
        elif (df.loc[i, 'y'] >= 65535):
            df.loc[i, 'y'] = None

    particle_num = 5
    particle_dim = 3
    iter_num = 5
    c1 = 2
    c2 = 2
    w = 0.5
    max_value = int(len(alldataIndex) * 0.6)
    min_value = 0.01
    fdays = 0
    
    if (len(PSO_Params) != 0):
        particle_num = int(PSO_Params[0])
        iter_num = int(PSO_Params[1])
        min_value = float(PSO_Params[2])
        c1 = float(PSO_Params[3])
        c2 = float(PSO_Params[4])
        w = float(PSO_Params[5])
    print("Final PSO_Num: ", particle_num)
    print("Final PSO_Dim: ", particle_dim)
    print("Final PSO_IterNum: ", iter_num)
    print("Final PSO_Max: ", max_value)
    print("Final PSO_Min: ", min_value)
    print("Final PSO_LocalLR: ", c1)
    print("Final PSO_GlobalLR: ", c2)
    print("Final PSO_Inertial: ", w)

    pso = PSO(particle_num, particle_dim, iter_num, c1, c2, w, max_value, min_value, df, fdays, alldataIndex)

    glo_gbest_parameter = pso.main()

    m = Prophet(seasonality_mode="additive", seasonality_prior_scale=glo_gbest_parameter[0],
                changepoint_prior_scale=glo_gbest_parameter[1], n_changepoints=glo_gbest_parameter[2],
                changepoint_range=1, daily_seasonality=False, weekly_seasonality=False)

    m.fit(df)
    fday = 0
    future = m.make_future_dataframe(periods=fday, freq='D')
    forecast = m.predict(future)

    if (flag):
        m.plot(forecast)
        plt.xlabel("Date", fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"),fontsize=16)
        plt.ylabel("Artificial Light Radiance", fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"),fontsize=16)
        #plt.legend(loc='lower left', prop={'size': 16, "family": "Times New Roman"})  # SimHei
        plt.yticks(fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        plt.xticks(fontproperties=font_manager.FontProperties(
            fname="C:/Users/jmh1998/AppData/Local/Microsoft/Windows/Fonts/AdobeGothicStd-Bold.otf"))
        plt.tick_params(labelsize=16)
        plt.savefig(pic_save_dir+"\\"+key+".png",bbox_inches='tight')

    mape = mean_forecast_err1(training_NTLValues, alldataIndex, forecast[['ds', 'yhat']])
    print("mape:", mape)

    relative_error_once = mape / np.mean(training_NTLValues)
    print("relative error:", relative_error_once)

    datafilling_TS = getDatafillingTS(df, forecast, len(time_series))

    return [datafilling_TS, key]

def writeDatafillingResult(f,res,time_list):
    f.write("pointNum:YYYYMMDD,NTLValue;..." + "\n")
    for i in range(len(res)):
        lizt = res[i].get()
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

def error_callback(e):
    print('error_callback: ', e)

if __name__=="__main__":
    # name_list = ["Adiyaman",
    #              "Aleppo",
    #              "Antakya",
    #              "Gaziantep",
    #              "Kahramanmaras",
    #              "Kirikhan",
    #              "Latakia",
    #              "Samandag"]
    # name_list = [
    #              "Kirikhan",
    #              "Antakya",
    #              "Samandag",
    #              "Adiyaman",
    #              "Kahramanmaras"]
    name_list = [
                 "Samandag",
                 ]
    parent_dir = "G:\\postgraduate\\postgraduate_bishe\\"
    # time_series_type = "TS_Txt_Constrained_By_LC_Larger50%_1_1_20220902_20240208"
    time_series_type = "TS_Txt_1_1_20220902_20240208"

    start_time = "20220902"
    end_time = "20240208"

    for name in name_list:
        # file_path = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_"+str(name)
        file_path = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_" + str(name)
        datasets = loadData(file_path, start_time, end_time)
        # datasets = loadData(file_path)

        pic_save_dir = parent_dir + time_series_type
        PSO_Params = [2, 2, 0.01, 2, 2, 0.5]

        start = time.time()  # 主进程1
        pool = multiprocessing.Pool(8)
        results = []

        for i in range(len(datasets)):
            key_list = datasets[i][-1]
            eachPixel = datasets[i]
            # 返回就是补值的时间序列，只不过需要用get方法获取里面的list值
            result = pool.apply_async(func=fit_prophet_getTS,
                                      args=(eachPixel[0],
                                            eachPixel[1],
                                            eachPixel[2],
                                            PSO_Params,
                                            key_list[i],
                                            False,
                                            pic_save_dir),
                                      error_callback=error_callback)
            results.append(result)
        pool.close()
        pool.join()
        print('时间消耗是：', time.time() - start)

        # 结果写入文件
        outputFile = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_"+str(name)+"_more50_wholeSeries_Prophet_beforefit"
        f = open(outputFile, 'w')
        time_list = []
        if (len(datasets)):
            time_list = datasets[0][0]
        writeDatafillingResult(f, results, time_list)
        print('finished：', outputFile)