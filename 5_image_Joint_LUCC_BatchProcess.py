#/usr/bin/env python
# -*- coding: UTF-8 -*-

import glob
import os
import gdal
import math
import arcpy
from arcpy import env

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

def generateTIFFilePath(folderPath):
    # 利用glob包，将inws下的所有tif文件读存放到rasters中
    rasters = glob.glob(os.path.join(folderPath, "*.tif"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][:-4]
        Name_List.append(Name)
    return rasters, Name_List

# 有投影的拼接会出现错误，需要重投影（Arcpy实现或GDAL WARP坐标转换）
# !!!!! 处理DNB的代码
if __name__ == "__main__":
    # 只需要把事件 Event, File_Type
    # 设置好即可得到每一天NTL影像与掩码影像拼接后的影像，影像保存在Country_Name_shorthand文件夹下，用joint命名表示
    ## 注：该拼接方法是将一个国家所有的事件数据都进行拼接
    Event = "LUCC"
    File_Type = "VNP46A2"
    Country_Code = "PRI"

    # 构建工作路径，并生成需要拼接的数据所在的文件夹
    work_dic = "D:\\VZA_Article\\data\\" + Event + "\\" + Country_Code + "\\"
    dirs_list = getDirs(work_dic)
    Joint_Images_Path_List = []
    Name = ""
    for dir in dirs_list:
        if (Name == ""):
            Name = dir.split("_")[-1]
        print (dir + " has started...")

        tif_dir = work_dic + dir + "\\"
        tif_paths, tif_names = generateTIFFilePath(tif_dir)
        Joint_Images_Path_List.append(tif_paths[0])

    Output_NTL_dic = work_dic
    # 这一天至少有一个tile需要拼接，如果都没有表明这一天该区域数据全部缺失
    input_files_str = ""
    if (len(Joint_Images_Path_List) != 0):
        for i in range(len(Joint_Images_Path_List)):
            if (i != len(Joint_Images_Path_List) - 1):
                input_files_str += Joint_Images_Path_List[i] + ";"
            else:
                input_files_str += Joint_Images_Path_List[i]
    print (input_files_str)

    sr = arcpy.SpatialReference(4326)
    arcpy.MosaicToNewRaster_management(input_files_str, Output_NTL_dic,
                                       Country_Code+"_"+Name+"_merge_image.tif", sr,
                                       "8_BIT_UNSIGNED", number_of_bands="1", mosaic_method="LAST", mosaic_colormap_mode="FIRST")
