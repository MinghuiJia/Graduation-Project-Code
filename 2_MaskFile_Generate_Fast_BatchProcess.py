#/usr/bin/env python
# -*- coding: UTF-8 -*-
import glob
import os
import gdal
import numpy as np
import arcpy
from arcpy import env
from gdalconst import *

# 读取tiff文件
def read_tiff(filename):
    datasets=gdal.Open(filename)  # 读取文件
    row=datasets.RasterXSize    # 获取数据的宽
    col=datasets.RasterYSize    # 获取数据的高
    band=datasets.RasterCount   # 获取数据的波段数

    geoTransform = datasets.GetGeoTransform()   # 仿射矩阵
    proj = datasets.GetProjection()     # 获取投影信息
    dt = datasets.GetRasterBand(1)  # 读取i+1波段信息（读取时从1开始）
    NaN_Value = dt.GetNoDataValue() # 得到影像中nodata的数值
    data = dt.ReadAsArray(0,0,row,col) # Getting data from 0 rows and 0 columns
    del datasets
    return data,geoTransform,proj, NaN_Value

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
    outband.SetNoDataValue(0)   # 将影像的某个值设置为nodata
    outband.WriteArray(array)   #将数据写入获取的这个波段中（写入的数据只能是二维的）
    outRaster.FlushCache()
    del outRaster

# 生成每个文件的读取路径及文件名
def generateTIFFilePath(folderPath):
    # 利用glob包，将inws下的所有tif文件读存放到rasters中
    rasters = glob.glob(os.path.join(folderPath, "*.tif"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][-36:-22]
        Name_List.append(Name)
    return rasters, Name_List

# 根据各位设置情况生成10进制的云层掩码值
def generateCloudMaskValue(Cloud_Bit_Setting):
    result_list = [[]]
    for key in Cloud_Bit_Setting:
        list_count = len(result_list)
        for j in range(list_count):
            temp_list = result_list.pop(0)
            for i in range(len(Cloud_Bit_Setting[key])):
                result_list.append(temp_list + Cloud_Bit_Setting[key][i])

    CloudMask_Values_10_List = []
    for i in range(len(result_list)):
        bin_str = ''.join('%s' %id for id in result_list[i])
        CloudMask_Values_10_List.append(int(bin_str, 2))
    return CloudMask_Values_10_List

# 删除文件夹中文件的代码
def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)

# 生成多种限制条件的掩码文件，1有效，0无效
def generateMaskFiles(CloudMask_Files, CloudMask_Files_Name, MQ_Files, SC_Files, SZA_Files, Cloud_Bit_Setting, outputFile_dic):

    # 基于设置情况，生成云层掩码的10进制数
    CloudMask_Values_10_List = generateCloudMaskValue(Cloud_Bit_Setting)
    # print (CloudMask_Values_10_List)
    # 构建判断条件
    ConditionEquation_str = ""
    for i in range(len(CloudMask_Values_10_List)):
        if (i == 0):
            ConditionEquation_str += "VALUE <> " + str(CloudMask_Values_10_List[i])
        else:
            ConditionEquation_str += " And VALUE <> " + str(CloudMask_Values_10_List[i])
    # print (ConditionEquation_str)

    # 用于存放临时文件的
    output_dic = outputFile_dic + "temp\\"
    # 判断输出路径的文件夹是否存在，不存在则创建一个
    if not os.path.exists(output_dic):
        os.makedirs(output_dic)

    # 逐文件遍历处理
    for i in range(len(CloudMask_Files)):
        # 根据文件名称解析tile和时间DOY
        Name_List = CloudMask_Files_Name[i].split(".")
        Tiles = Name_List[1]
        DOY = Name_List[0]

        # 云层掩码提取
        # print (CloudMask_Files[i])
        outSetNull_CloudMask = arcpy.sa.SetNull(CloudMask_Files[i], 1, ConditionEquation_str)
        output_path_CloudMask = output_dic + DOY + "_" + Tiles + "_CloudMask.tif"
        outSetNull_CloudMask.save(output_path_CloudMask)
        # print (outSetNull_CloudMask)
        raster_CloudMask, geoTransform_CloudMask, proj_CloudMask, NaN_Value_CloudMask = read_tiff(output_path_CloudMask)
        raster_CloudMask[raster_CloudMask == NaN_Value_CloudMask] = 0
        # raster_CloudMask = arcpy.Raster(output_path_CloudMask)
        # print (raster_CloudMask)

        # 强制性质量指标提取
        # print (MQ_Files[i])
        outSetNull_MQ = arcpy.sa.SetNull(MQ_Files[i], 1 ,"VALUE = 1 Or VALUE = 2 Or VALUE = 255")
        output_path_MQ = output_dic + DOY + "_" + Tiles + "_MQ.tif"
        outSetNull_MQ.save(output_path_MQ)
        # print (outSetNull_MQ)
        raster_MQ, geoTransform_MQ, proj_MQ, NaN_Value_MQ = read_tiff(output_path_MQ)
        raster_MQ[raster_MQ == NaN_Value_MQ] = 0
        # raster_MQ = arcpy.Raster(output_path_MQ)
        # print (raster_MQ)

        # 雪覆盖掩码提取
        # print (SC_Files[i])
        outSetNull_SC = arcpy.sa.SetNull(SC_Files[i], 1, "VALUE = 1 Or VALUE = 255")
        output_path_SC = output_dic + DOY + "_" + Tiles + "_SC.tif"
        outSetNull_SC.save(output_path_SC)
        # print (outSetNull_SC)
        raster_SC, geoTransform_SC, proj_SC, NaN_Value_SC = read_tiff(output_path_SC)
        raster_SC[raster_SC == NaN_Value_SC] = 0
        # raster_SC = arcpy.Raster(output_path_SC)
        # print (raster_SC)

        # 太阳天顶角筛选提取
        # print (SC_Files[i])
        outSetNull_SZA = arcpy.sa.SetNull(SZA_Files[i], 1, "VALUE <= 10800")
        output_path_SZA = output_dic + DOY + "_" + Tiles + "_SZA.tif"
        outSetNull_SZA.save(output_path_SZA)
        # print (outSetNull_SC)
        raster_SZA, geoTransform_SZA, proj_SZA, NaN_Value_SZA = read_tiff(output_path_SZA)
        raster_SZA[raster_SZA == NaN_Value_SZA] = 0
        # raster_SC = arcpy.Raster(output_path_SC)
        # print (raster_SC)

        Mask_Array = raster_CloudMask * raster_MQ * raster_SC * raster_SZA
        array2raster(outputFile_dic + DOY + "_" + Tiles + "_Mask.tif",Mask_Array,geoTransform_SC, proj_SC)
        # Mask_Array.save(outputFile_dic + Country_Name_shorthand + "_" + DOY + "_" + Tiles + "_Mask.tif")
        print(DOY + "_" + Tiles + "_Mask.tif File has been Generated...")

    # del_file(output_dic)

# def getDirs(work_dic):
#     iter_i = 0
#     dirs_list = []
#     for fpath, dirname, fnames in os.walk(work_dic):
#         if (iter_i > 0):
#             dirs_list.append(fpath)
#         iter_i += 1
#     return dirs_list

def getDirs(path):
    # 定义一个列表，用来存储结果
    list = []
    # 判断路径是否存在
    if (os.path.exists(path)):
        # 获取该目录下的所有文件或文件夹目录
        files = os.listdir(path)
        for file in files:
            # 得到该文件下所有目录的路径
            m = os.path.join(path, file)
            # 判断该路径下是否是文件夹
            if (os.path.isdir(m)):
                h = os.path.split(m)
                list.append(h[1])
        return list


arcpy.CheckOutExtension("Spatial")

if __name__ == "__main__":
    File_Type = ["VNP46A2_res_res","VNP46A1_res_res"]
    Cloud_Bit_Setting = {
        6: [[0]],  # "Day/Night"
        5: [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 1]],  # "Land/Water Background"
        4: [[1, 1], [1, 0]],  # "Cloud Mask Quality"
        3: [[0, 0]],  # "Cloud Detection Results & Confidence Indicato"
        2: [[0]],  # "Shadow Detected"
        1: [[0]],  # "Cirrus Detection (IR) (BTM15 – BTM16)"
        0: [[0]]  # "Snow/ Ice Surface"
    }

    # 构建工作路径，并生成需要获取的数据所在的文件夹
    work_dic = "G:\\postgraduate\\postgraduate_bishe"

    tif_dir = work_dic + "\\" + File_Type[0] + "_tif"

    # 构建需要读取的限制条件影像文件夹路径，以及保存掩码文件的文件夹路径
    work_dic_CloudMask = tif_dir + "\\QF_Cloud_Mask\\"
    work_dic_Mandatory_Quality = tif_dir + "\\Mandatory_Quality_Flag\\"
    work_dic_SnowCover = tif_dir + "\\Snow_Flag\\"

    MaskFile_Output_dic = tif_dir + "\\MaskFile\\"

    tif_dir = work_dic + "\\" + File_Type[1] + "_tif"
    work_dic_SolarZenith = tif_dir + "\\Solar_Zenith\\"

    # 判断输出路径的文件夹是否存在，不存在则创建一个
    if not os.path.exists(MaskFile_Output_dic):
        os.makedirs(MaskFile_Output_dic)

    # 从文件夹中获取需要处理的所有文件路径，以及文件名
    GeotiffFiles_CloudMask, FileName_CloudMask = generateTIFFilePath(work_dic_CloudMask)
    GeotiffFiles_MQ, FileName_MQ = generateTIFFilePath(work_dic_Mandatory_Quality)
    GeotiffFiles_SC, FileName_SC = generateTIFFilePath(work_dic_SnowCover)
    GeotiffFiles_SZA, FileName_SAZ = generateTIFFilePath(work_dic_SolarZenith)

    # 生成掩码文件
    generateMaskFiles(GeotiffFiles_CloudMask, FileName_CloudMask, GeotiffFiles_MQ, GeotiffFiles_SC, GeotiffFiles_SZA,
                        Cloud_Bit_Setting, MaskFile_Output_dic)

    print (MaskFile_Output_dic + " has been generated...")

