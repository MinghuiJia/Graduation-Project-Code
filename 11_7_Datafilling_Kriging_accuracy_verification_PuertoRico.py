import math

import pandas as pd
from pykrige.ok import OrdinaryKriging
import numpy as np

from dataloader_with_time1 import loadData

def findPointIndex(r, validation_index):
    point_index = []
    for i in range(len(validation_index)):
        if (r in validation_index[i]):
            point_index.append(i)
    return point_index
def fit_kriging(df, validation_index, lng_list, lat_list):
    row, col = df.shape
    relative_error_list = []
    for r in range(row):
        # 寻找该时刻下，是否有被掩掉的像素
        point_index = findPointIndex(r, validation_index)
        # 如果有，就进行补值，并计算误差
        if (len(point_index)):
            row_values = df.loc[[r]].values[:,1:]

            lons = []
            lats = []
            datas = []
            value_dict = {}
            for k in range(len(lng_list)):
                # 表明这些点是要被掩掉的
                if (k in point_index):
                    value_dict[k] = row_values[0][k]
                elif (row_values[0][k] < 65535):
                    lons.append(lng_list[k])
                    lats.append(lat_list[k])
                    datas.append(row_values[0][k])

            # 这里要求像素数量要大于1
            if (len(lons) > 2):
                # 使用克里金插值方法进行补值
                OK = OrdinaryKriging(lons, lats, datas, variogram_model='hole-effect', nlags=1)
                z1, ss1 = OK.execute('points', lng_list, lat_list)
                pred_values = z1.flatten()

                # 计算相对误差
                relative_error = 0
                for k in range(len(point_index)):
                    true_value = value_dict[point_index[k]]
                    pred_value = pred_values[point_index[k]]

                    relative_error += math.fabs(true_value-pred_value) / true_value
                relative_error = relative_error / len(point_index)
                # if (relative_error < 1):
                relative_error_list.append(relative_error)

    average_relative_error = 0
    if (len(relative_error_list)):
        average_relative_error = np.mean(relative_error_list)
    return average_relative_error

def testKriging():
    df = pd.read_excel('C:\\Users\\jmh1998\\Desktop\\kiring\\meiyu_sh_2020.xlsx')
    # 读取站点经度
    lons = df['lon']
    # 读取站点纬度
    lats = df['lat']
    # 读取梅雨量数据
    data = df['meiyu']

    # 生成经纬度网格点
    grid_lon = np.linspace(120.8, 122.1, 1300)
    grid_lat = np.linspace(30.6, 31.9, 1300)

    OK = OrdinaryKriging(lons, lats, data, variogram_model='gaussian', nlags=6)
    z1, ss1 = OK.execute('grid', grid_lon, grid_lat)
    cc = z1.shape

    # 转换成网格
    xgrid, ygrid = np.meshgrid(grid_lon, grid_lat)
    # 将插值网格数据整理
    df_grid = pd.DataFrame(dict(long=xgrid.flatten(), lat=ygrid.flatten()))
    # 添加插值结果
    df_grid["Krig_gaussian"] = z1.flatten()

    aaa = 10

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

def dataConvert(datasets):
    key_list = []
    lng_lat_list = []
    time_list = []
    lng_list = []
    lat_list = []
    # 获取时间、像素、经纬度列表
    if (len(datasets)):
        time_list = datasets[0][0]
        key_list = datasets[0][-1]
        lng_lat_list = datasets[0][-2]

    # 解析经纬度，分成经度和维度列表
    for i in range(len(lng_lat_list)):
        lng_lat = lng_lat_list[i].split(',')
        lng = float(lng_lat[0])
        lng_list.append(lng)
        lat = float(lng_lat[1])
        lat_list.append(lat)

    column_name = ['time'] + key_list
    column_value = [time_list]

    all_data_index = []
    all_crossValidation_trianingData_Index = []
    all_crossValidation_validationData_Index = []
    for i in range(len(datasets)):
        column_value.append(datasets[i][1])

        all_data_index.append(datasets[i][2])
        all_crossValidation_trianingData_Index.append(datasets[i][3])
        all_crossValidation_validationData_Index.append(datasets[i][4])
    index_datasets = [all_data_index, all_crossValidation_trianingData_Index, all_crossValidation_validationData_Index]

    column_value = tuple(column_value)
    df = pd.DataFrame(np.vstack(column_value).T, columns=column_name)

    return df, index_datasets, lng_list, lat_list

if __name__ == "__main__":
    testKriging()
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
        file_path = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_" + str(name)
        datasets = loadData(file_path, start_time, end_time)

        # datasets转成dataframe格式
        df, index_datasets, lng_list, lat_list = dataConvert(datasets)

        # 进行补值精度验证
        accuracy_list = []
        # 由于每个像素缺失的不一致，所以需要取最少的次数
        cross_validation_count = len(index_datasets[1][0])
        for i in range(len(index_datasets[1])):
            temp = len(index_datasets[1][i])
            if (temp < cross_validation_count):
                cross_validation_count = temp

        # 每个像素的补值精度（交叉验证次数）
        results = []
        for j in range(cross_validation_count):
            training_index = []
            validation_index = []
            for pointNum in range(len(datasets)):
                # train
                training_index.append(index_datasets[1][pointNum][j])
                # validation
                validation_index.append(index_datasets[2][pointNum][j])

            error = fit_kriging(df, validation_index, lng_list, lat_list)
            results.append(error)

        average_error = np.mean(results)

        # 结果写入文件
        outputFile = parent_dir + time_series_type + "\\TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_" + str(name) + "_more50_Kriging_accuracy_error_afterfit"
        f = open(outputFile, 'w')
        f.write("mean_error:" + str(average_error) + "\n")
        print('finished：', outputFile)
        f.close()