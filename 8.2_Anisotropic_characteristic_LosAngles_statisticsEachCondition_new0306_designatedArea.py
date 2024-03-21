# -*- coding: utf-8 -*-
# 筛选符合需求的数据，统计每个筛选条件下满足要求的数据的时间，并保存到excel

import gdal
import numpy as np
import os
import matplotlib.pyplot as plt
import re
import math
import xlwt

Events_Gadm_Level_List = {
    # "SYR_20220101_20230301": {"Adm_urban": ["Adiyaman",
    #                                         "Aleppo",
    #                                         "Antakya",
    #                                         "Gaziantep",
    #                                         "Kahramanmaras",
    #                                         "Kirikhan",
    #                                         "Latakia",
    #                                         "Samandag"]},
    "TURSYR_20220101_20240208": {"Adm_urban": ["Adiyaman",
                                            "Antakya",
                                            "Kahramanmaras",
                                            "Kirikhan",
                                            "Samandag"]},
}

# 读取tiff文件
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

# 写入tiff文件
def array2raster(outpath,array,geoTransform,proj):
    if 'int8' in array.dtype.name:  # 判断栅格数据的数据类型
        datatype = gdal.GDT_Byte
    elif 'int16' in array.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    cols=array.shape[1]
    rows=array.shape[0]
    driver=gdal.GetDriverByName('Gtiff')
    outRaster=driver.Create(outpath,cols,rows,1,datatype)
    outRaster.SetGeoTransform(geoTransform)#参数2,6为水平垂直分辨率，参数3,5表示图片是指北的
    outRaster.SetProjection(proj)#将几何对象的数据导出为wkt格式
    outband=outRaster.GetRasterBand(1)  #获取已经创建好的一个波段
    outband.WriteArray(array)   #将数据写入获取的这个波段中（写入的数据只能是二维的）
    outRaster.FlushCache()
    del outRaster

# 计算经纬度坐标所对应的列号
def calTiffCol(lng,lat,GeoTransform):
    temp = GeoTransform[1]*GeoTransform[5] - GeoTransform[2]*GeoTransform[4]
    col = int((GeoTransform[5]*(lng-GeoTransform[0]) - GeoTransform[2]*(lat-GeoTransform[3])) / temp)
    return col

# 计算经纬度坐标所对应的行号
def calTiffRow(lng,lat,GeoTransform):
    temp = GeoTransform[1]*GeoTransform[5] - GeoTransform[2]*GeoTransform[4]
    row = int((GeoTransform[1]*(lat-GeoTransform[3]) - GeoTransform[4]*(lng-GeoTransform[0])) / temp)
    return row

# 根据行列号计算对应的经纬度
def calTifLngLat(col, row, GeoTransform):
    lng = GeoTransform[0] + col * GeoTransform[1] + row * GeoTransform[2]
    lat = GeoTransform[3] + col * GeoTransform[4] + row * GeoTransform[5]
    return lng, lat

# 统计窗口的创建（该方式只适用于边长为奇数的窗口创建）
def windowCreate(winsize,row,col):
    window = []
    row_start = row - int((winsize - 1) / 2)
    row_end = row_start + winsize
    col_start = col - int((winsize - 1) / 2)
    col_end = col_start + winsize
    for row_index in range(row_start, row_end):
        for col_index in range(col_start, col_end):
            window.append([col_index, row_index])
    return window

# 利用QF_Cloud_Mask筛选高质量数据
def meetRequirementsOfQF_Cloud_Mask(data_QF_Cloud_Mask,window,pixel_index):
    row = window[pixel_index][1]
    col = window[pixel_index][0]
    QF_Cloud_Mask_Value = data_QF_Cloud_Mask[row][col]
    binary_index= 10
    binary_array = [0] * 11     #创建一个11位的数组并初始化为0
    while(QF_Cloud_Mask_Value != 0):
        binary_array[binary_index] = QF_Cloud_Mask_Value % 2
        QF_Cloud_Mask_Value = QF_Cloud_Mask_Value // 2
        binary_index -= 1

    #高位补0
    while(binary_index > -1):
        binary_array[binary_index] = 0
        binary_index -= 1

    # 判断是否满足需求
    # if (binary_array[1] == 0 and binary_array[2] == 0 and binary_array[3] == 0 and
    #     binary_array[4] == 0 and binary_array[5] == 1 and (binary_array[6] == 0 or binary_array[6] == 1) and
    #     (not (binary_array[7] == 0 and binary_array[8] == 1 and binary_array[9] == 1)) and binary_array[10] == 0):
    if (binary_array[0] == 0 and binary_array[1] == 0 and binary_array[2] == 0 and binary_array[3] == 0 and
        binary_array[4] == 0 and binary_array[5] == 1 and (binary_array[6] == 0 or binary_array[6] == 1) and
        (not (binary_array[7] == 0 and binary_array[8] == 1 and binary_array[9] == 1)) and binary_array[10] == 0):
        return True
    else:
        return False

# 日期转换:年历日转换成YYYMMDD
def timeTransform(strTime):
    YYYYMMDD = [0] * 3
    YYYYMMDD[0] = int(strTime[:4])
    day = int(strTime[4:])
    febday = 28
    if (int(YYYYMMDD[0]) % 4 == 0):
        febday = 29
    if (day > 0 and day <= 31):
        YYYYMMDD[1] = 1
        YYYYMMDD[2] = day
    elif (day > 31 and day <= (31 + febday)):
        YYYYMMDD[1] = 2
        YYYYMMDD[2] = day - 31
    elif (day > (31 + febday) and day <= (62 + febday)):
        YYYYMMDD[1] = 3
        YYYYMMDD[2] = day - (31 + febday)
    elif (day > (62 + febday) and day <= (92 + febday)):
        YYYYMMDD[1] = 4
        YYYYMMDD[2] = day - (62 + febday)
    elif (day > (92 + febday) and day <= (123 + febday)):
        YYYYMMDD[1] = 5
        YYYYMMDD[2] = day - (92 + febday)
    elif (day > (123 + febday) and day <= (153 + febday)):
        YYYYMMDD[1] = 6
        YYYYMMDD[2] = day - (123 + febday)
    elif (day > (153 + febday) and day <= (184 + febday)):
        YYYYMMDD[1] = 7
        YYYYMMDD[2] = day - (153 + febday)
    elif (day > (184 + febday) and day <= (215 + febday)):
        YYYYMMDD[1] = 8
        YYYYMMDD[2] = day - (184 + febday)
    elif (day > (215 + febday) and day <= (245 + febday)):
        YYYYMMDD[1] = 9
        YYYYMMDD[2] = day - (215 + febday)
    elif (day > (245 + febday) and day <= (276 + febday)):
        YYYYMMDD[1] = 10
        YYYYMMDD[2] = day - (245 + febday)
    elif (day > (276 + febday) and day <= (306 + febday)):
        YYYYMMDD[1] = 11
        YYYYMMDD[2] = day - (276 + febday)
    elif (day > (306 + febday) and day <= (337 + febday)):
        YYYYMMDD[1] = 12
        YYYYMMDD[2] = day - (306 + febday)
    ymdStr = ""
    yearNum = len(str(YYYYMMDD[0]))
    if (yearNum != 4):
        for yNum in range(4 - yearNum):
            ymdStr += "0"
    ymdStr += str(YYYYMMDD[0])

    monthNum = len(str(YYYYMMDD[1]))
    if (monthNum != 2):
        for mNum in range(2 - monthNum):
            ymdStr += "0"
    ymdStr += str(YYYYMMDD[1])

    dayNum = len(str(YYYYMMDD[2]))
    if (dayNum != 2):
        for dNum in range(2 - dayNum):
            ymdStr += "0"
    ymdStr += str(YYYYMMDD[2])
    return ymdStr

# 筛选的数据保存在文件中
def savePoints(result_array,statistics_points,statistics_points_col_row,output_dic):
    #创建文件
    f = open(output_dic,'w')
    # content_str = ""
    # write_content = []
    # for temp_i in range(len(statistics_points)):
    #     if (temp_i == 0):
    #         pass
    #         # content_str += "point " + str(temp_i+1) + ":" + str(statistics_points[temp_i][0]) + "," + str(statistics_points[temp_i][1])
    #     else:
    #         content_str += ";" + "point " + str(temp_i+1) + ":" + str(statistics_points[temp_i][0]) + "," + str(statistics_points[temp_i][1])
    #     write_content.append("point "+str(temp_i+1)+"'s Time")
    #     write_content.append("point "+str(temp_i+1)+"'s ZenithAngle")
    #     write_content.append("point "+str(temp_i+1)+"'s NTLValue")
    # f.write(content_str + "\n")
    f.write("pointNum:lng,lat(left top):YYYYMMDD,Zenith,NTLValue;..."+"\n")

    point_id = 0
    for i in range(len(result_array)):
        # 这里可以设置具体的限制，当数据少于多少就不补值了
        if (len(result_array[i]) < 10):
            continue
        f.write("point " + str(point_id + 1) + ":" + str(statistics_points[i][0]) + "," + str(statistics_points[i][1]) + ":")
        for j in range(len(result_array[i])):
            if (j == 0):
                f.write(result_array[i][j][2]+","+str(result_array[i][j][1])+","+str(result_array[i][j][0]))
            else:
                f.write(";"+result_array[i][j][2]+","+str(result_array[i][j][1])+","+str(result_array[i][j][0]))
        f.write("\n")
        point_id += 1

    f.close()

# 分析天顶角和夜间灯光辐射度之间的相关性
def Statistics_Correlation_With_Zenith_And_NTL(GeotiffFiles_ntl, GeotiffFiles_vza, GeotiffFiles_mask, output_dic):
    print(GeotiffFiles_ntl)
    print(GeotiffFiles_vza)
    print(GeotiffFiles_mask)

    # 无效数据是0，65535,计算该区域需要计算的所有点的行列号
    statistics_points_col_row = []
    data_DNB, geoTransform_DNB, proj_DNB = read_tiff(GeotiffFiles_ntl[0])
    data_DNB_2dim = data_DNB[:, :, 0]
    for i in range(len(data_DNB_2dim)):
        for j in range(len(data_DNB_2dim[0])):
            if (data_DNB_2dim[i][j] != 0):
                statistics_points_col_row.append([j,i])
    print(statistics_points_col_row)
    print(len(statistics_points_col_row))
    result_array = []
    for i in range(len(statistics_points_col_row)):
        result_array.append([])

    GeoTransform_Ref = ""
    for k in range(len(GeotiffFiles_ntl)):
        #读取Geotiff
        #提取文件名中的日期转换成YYYYMMDD格式
        strTime = re.search(r'[0-9]{7}',GeotiffFiles_ntl[k].split("\\")[-1]).group(0)
        YYYMMDDTime = timeTransform(strTime)
        # print(YYYMMDDTime)

        data_DNB, geoTransform_DNB, proj_DNB = read_tiff(GeotiffFiles_ntl[k])
        data_Zenith_Angle, geoTransform_Zenith_Angle, proj_Zenith_Angle = read_tiff(GeotiffFiles_vza[k])
        data_Mask, geoTransform_Mask, proj_Mandatory_Mask = read_tiff(GeotiffFiles_mask[k])

        if (k == 0):
            GeoTransform_Ref = geoTransform_DNB

        statistics_points = statistics_points_col_row

        # 3维转二维，即band为1
        data_DNB_2dim = data_DNB[:, :, 0]
        data_Mask_2dim = data_Mask[:, :, 0]
        data_Zenith_Angle_2dim = data_Zenith_Angle[:, :, 0]

        #统计采样区域，同时要保证窗口内的像素都没有被污染
        for p in range(len(statistics_points)):
            col_row = statistics_points[p]
            #创建3*3窗口，统计里面的信息
            winsize = 1
            window = windowCreate(winsize,col_row[1],col_row[0])
            # print(window)

            # 需要先判断一下当前像素位置的窗口内是否有像素值为0的，代表该像素不能用，因为不规则裁剪
            pixelFlag = True
            MaskFlag = True
            for eachi in range(len(window)):
                if (data_DNB_2dim[window[eachi][1]][window[eachi][0]] <= 0 or
                        data_Mask_2dim[window[eachi][1]][window[eachi][0]] != 1):
                    pixelFlag = False
                    MaskFlag = False
                    break

            if (pixelFlag == True and MaskFlag == True):  #如果窗口内都没有被污染，统计均值
                DNB_average = 0
                for j in range(len(window)):
                    DNB_average += data_DNB_2dim[window[j][1]][window[j][0]]
                DNB_average = (DNB_average / len(window)) / 10
                Angle = data_Zenith_Angle_2dim[col_row[1]][col_row[0]] / 100
                result_array[p].append([DNB_average,Angle,YYYMMDDTime])
            else:
                print("Geotiff image " + str(k+1) + " has dirty pixel...")

        print("finished " + str(k+1) + " Geotiff image...")
    print(result_array)
    for i in range(len(result_array)):
        print("point "+str(i+1)+" count: " + str(len(result_array[i])))

    # 保存生成的点
    statistics_points_lnglat = []
    for point_lng_lat in statistics_points_col_row:
        lng, lat = calTifLngLat(point_lng_lat[0], point_lng_lat[1], GeoTransform_Ref)
        statistics_points_lnglat.append([lng, lat])
    savePoints(result_array,statistics_points_lnglat,statistics_points_col_row,output_dic)

# 生成每个文件的读取路径
def generateFilePath(folderPath):
    GeotiffFiles = os.listdir(folderPath)  # 返回当前工作目录下的文件列表
    Result_GeoTiffFiles = []
    for i in range(len(GeotiffFiles)):
        if (GeotiffFiles[i][-4:] == ".tif"):
            Result_GeoTiffFiles.append(folderPath + GeotiffFiles[i])
            # GeotiffFiles[i] = folderPath + GeotiffFiles[i]
    return Result_GeoTiffFiles

# 设置具体的限制，当数据少于多少就不写入时间序列
if __name__=="__main__":
    gdal.AllRegister()  # 注册驱动

    # 构建工作路径，并生成需要获取的数据所在的文件夹
    work_dic = work_dic = "G:\\postgraduate\\postgraduate_bishe\\"

    for key in sorted (Events_Gadm_Level_List):
        for adm_type in sorted(Events_Gadm_Level_List[key]):
            for adm_shp_name in Events_Gadm_Level_List[key][adm_type]:
                Gadm_Name = adm_shp_name
                eventID_startTime_endTime = key
                print(Gadm_Name, eventID_startTime_endTime)

                # 基于Country_Name_shorthand解析出国家缩写，数据收集的开始与结束时间
                eventID_startTime_endTime_List = eventID_startTime_endTime.split("_")
                Start_Time_Str = eventID_startTime_endTime_List[1]
                End_Time_Str = eventID_startTime_endTime_List[2]
                Country_Code = eventID_startTime_endTime_List[0]

                # 需要读取的文件夹路径
                ntl_work_dic = work_dic + "\\VNP46A2_tif\\DNB_BRDF-Corrected_NTL_joint_clip_" + Gadm_Name + "_noTranslation\\"
                vza_work_dic = work_dic + "\\VNP46A1_tif\\Sensor_Zenith_joint_clip_" + Gadm_Name + "_noTranslation\\"
                # mask_work_dic = work_dic + "\\VNP46A2_tif\\MaskFile_joint_clip_" + Gadm_Name + "_noTranslation_Constrained_By_LC_Larger50%\\"
                mask_work_dic = work_dic + "\\VNP46A2_tif\\MaskFile_joint_clip_" + Gadm_Name + "_noTranslation\\"
                # output_dir = work_dic + "\\TS_Txt_Constrained_By_LC_Larger50%_1_1_20220902_20240208\\"
                output_dir = work_dic + "\\TS_Txt_1_1_20220902_20240208\\"
                # 判断输出路径的文件夹是否存在，不存在则创建一个
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                output_file_path = output_dir + "TS_output_withoutMoonIlluminationAndSnow_1%_1invalid_" + Gadm_Name

                # 组织每个文件的读取路径
                GeotiffFiles_ntl = generateFilePath(ntl_work_dic)
                GeotiffFiles_vza = generateFilePath(vza_work_dic)
                GeotiffFiles_mask = generateFilePath(mask_work_dic)

                # 分析天顶角和夜间灯光辐射度之间的相关性
                Statistics_Correlation_With_Zenith_And_NTL(GeotiffFiles_ntl, GeotiffFiles_vza, GeotiffFiles_mask, output_file_path)

