# -*- coding: utf-8 -*-

import gdal
import os

def readVNP46A2(work_dic,output_dic,science_datasetType):
    os.chdir(work_dic)
    rasterFiles = os.listdir(os.getcwd())  # 返回当前工作目录下的文件列表
    for i in range(len(rasterFiles)):
        if (rasterFiles[i][-3:] != ".h5"):
            continue

        rasterFilepre = rasterFiles[i][:-3]    #去掉后缀.h5
        # print(rasterFilepre)
        fileExtension = ".tif"

        # 打开hdf文件
        hdflayer = gdal.Open(rasterFiles[i], gdal.GA_ReadOnly)
        # 7个SDS（科学数据集）层

        # 获取子图层
        subhdflayer = ""
        if (science_datasetType == "DNB_BRDF-Corrected_NTL"):
            subhdflayer = hdflayer.GetSubDatasets()[0][0]
        elif (science_datasetType == "DNB_Lunar_Irradiance"):
            subhdflayer = hdflayer.GetSubDatasets()[1][0]
        elif (science_datasetType == "Gap_Filled_DNB_BRDF-Corrected_NTL"):
            subhdflayer = hdflayer.GetSubDatasets()[2][0]
        elif (science_datasetType == "Latest_High_Quality_Retrieval"):
            subhdflayer = hdflayer.GetSubDatasets()[3][0]
        elif (science_datasetType == "Mandatory_Quality_Flag"):
            subhdflayer = hdflayer.GetSubDatasets()[4][0]
        elif (science_datasetType == "QF_Cloud_Mask"):
            subhdflayer = hdflayer.GetSubDatasets()[5][0]
        elif (science_datasetType == "Snow_Flag"):
            subhdflayer = hdflayer.GetSubDatasets()[6][0]

        rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)   #打开子图层
        outputName = subhdflayer[92:]   #子图层的名称
        outputNameFinal = outputName + rasterFilepre + fileExtension
        # print(outputNameFinal)

        # 构建文件输出路径
        outputFolder = output_dic
        outputRaster = outputFolder + outputNameFinal

        # print(rlayer.GetMetadata_Dict())
        #获取影像四至范围
        HorizontalTileNumber = int(rlayer.GetMetadata_Dict()["HorizontalTileNumber"])
        VerticalTileNumber = int(rlayer.GetMetadata_Dict()["VerticalTileNumber"])

        WestBoundCoord = (10 * HorizontalTileNumber) - 180
        NorthBoundCoord = 90 - (10 * VerticalTileNumber)
        EastBoundCoord = WestBoundCoord + 10
        SouthBoundCoord = NorthBoundCoord - 10

        EPSG = "-a_srs EPSG:4326"  # WGS84
        translateOptionText = EPSG + " -a_ullr " + str(WestBoundCoord) + " " + str(NorthBoundCoord) + " " + str(EastBoundCoord) + " " + str(SouthBoundCoord)
        translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))
        gdal.Translate(outputRaster, rlayer, options=translateoptions)
        # gdal.Warp(outputRaster, rlayer)
        print(outputNameFinal, "has finished...")

def readVNP46A1(work_dic,output_dic,science_datasetType):
    os.chdir(work_dic)
    rasterFiles = os.listdir(os.getcwd())  # 返回当前工作目录下的文件列表
    for i in range(len(rasterFiles)):
        if (rasterFiles[i][-3:] != ".h5"):
            continue

        rasterFilepre = rasterFiles[i][:-3]
        # print(rasterFilepre)
        fileExtension = ".tif"

        # 打开hdf文件
        hdflayer = gdal.Open(rasterFiles[i], gdal.GA_ReadOnly)
        # 26个SDS（科学数据集）层
        # print(len(hdflayer.GetSubDatasets()))

        # 获取子图层
        subhdflayer = ""
        if (science_datasetType == "DNB_At_Sensor_Radiance_500m"):
            subhdflayer = hdflayer.GetSubDatasets()[4][0]
        elif (science_datasetType == "QF_Cloud_Mask"):
            subhdflayer = hdflayer.GetSubDatasets()[11][0]
        elif (science_datasetType == "Sensor_Azimuth"):
            subhdflayer = hdflayer.GetSubDatasets()[21][0]
        elif (science_datasetType == "Sensor_Zenith"):
            subhdflayer = hdflayer.GetSubDatasets()[22][0]
        elif (science_datasetType == "Glint_Angle"):
            subhdflayer = hdflayer.GetSubDatasets()[5][0]
        elif (science_datasetType == "Granule"):
            subhdflayer = hdflayer.GetSubDatasets()[6][0]
        elif (science_datasetType == "Lunar_Azimuth"):
            subhdflayer = hdflayer.GetSubDatasets()[7][0]
        elif (science_datasetType == "Lunar_Zenith"):
            subhdflayer = hdflayer.GetSubDatasets()[8][0]
        elif (science_datasetType == "Moon_Illumination_Fraction"):
            subhdflayer = hdflayer.GetSubDatasets()[9][0]
        elif (science_datasetType == "Moon_Phase_Angle"):
            subhdflayer = hdflayer.GetSubDatasets()[10][0]
        elif (science_datasetType == "QF_DNB"):
            subhdflayer = hdflayer.GetSubDatasets()[12][0]
        elif (science_datasetType == "Solar_Azimuth"):
            subhdflayer = hdflayer.GetSubDatasets()[23][0]
        elif (science_datasetType == "Solar_Zenith"):
            subhdflayer = hdflayer.GetSubDatasets()[24][0]
        elif (science_datasetType == "UTC_Time"):
            subhdflayer = hdflayer.GetSubDatasets()[25][0]
        else:
            print("no this type....")
            return 0

        rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)
        # 子图层的名称
        outputName = subhdflayer[92:]
        outputNameFinal = outputName + rasterFilepre + fileExtension
        # print(outputNameFinal)

        # 构建文件输出路径
        outputFolder = output_dic
        outputRaster = outputFolder + outputNameFinal

        # print(rlayer.GetMetadata_Dict())
        # 获取影像四至范围
        HorizontalTileNumber = int(rlayer.GetMetadata_Dict()["HorizontalTileNumber"])
        VerticalTileNumber = int(rlayer.GetMetadata_Dict()["VerticalTileNumber"])

        WestBoundCoord = (10 * HorizontalTileNumber) - 180
        NorthBoundCoord = 90 - (10 * VerticalTileNumber)
        EastBoundCoord = WestBoundCoord + 10
        SouthBoundCoord = NorthBoundCoord - 10

        EPSG = "-a_srs EPSG:4326"  # WGS84
        translateOptionText = EPSG + " -a_ullr " + str(WestBoundCoord) + " " + str(NorthBoundCoord) + " " + str(EastBoundCoord) + " " + str(SouthBoundCoord)
        translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))
        gdal.Translate(outputRaster, rlayer, options=translateoptions)
        # gdal.Warp(outputRaster, rlayer)
        print(outputNameFinal, "has finished...")

def readVNP46A4(work_dic,output_dic,science_datasetType):
    os.chdir(work_dic)
    rasterFiles = os.listdir(os.getcwd())  # 返回当前工作目录下的文件列表

    for i in range(len(rasterFiles)):
        rasterFilepre = rasterFiles[i][:-3]
        # print(rasterFilepre)
        fileExtension = ".tif"

        # 打开hdf文件
        hdflayer = gdal.Open(rasterFiles[i], gdal.GA_ReadOnly)

        # for kkk in range(len(hdflayer.GetSubDatasets())):
        #     print(kkk , " ", hdflayer.GetSubDatasets()[kkk][0])
        # # 26个SDS（科学数据集）层
        # print(len(hdflayer.GetSubDatasets()))

        # 获取子图层
        subhdflayer = ""
        if (science_datasetType == "AllAngle_Composite_Snow_Covered"):
            subhdflayer = hdflayer.GetSubDatasets()[0][0]
        elif (science_datasetType == "AllAngle_Composite_Snow_Covered_Num"):
            subhdflayer = hdflayer.GetSubDatasets()[1][0]
        elif (science_datasetType == "AllAngle_Composite_Snow_Covered_Quality"):
            subhdflayer = hdflayer.GetSubDatasets()[2][0]
        elif (science_datasetType == "AllAngle_Composite_Snow_Covered_Std"):
            subhdflayer = hdflayer.GetSubDatasets()[3][0]
        elif (science_datasetType == "AllAngle_Composite_Snow_Free"):
            subhdflayer = hdflayer.GetSubDatasets()[4][0]
        elif (science_datasetType == "AllAngle_Composite_Snow_Free_Num"):
            subhdflayer = hdflayer.GetSubDatasets()[5][0]
        elif (science_datasetType == "AllAngle_Composite_Snow_Free_Quality"):
            subhdflayer = hdflayer.GetSubDatasets()[6][0]
        elif (science_datasetType == "AllAngle_Composite_Snow_Free_Std"):
            subhdflayer = hdflayer.GetSubDatasets()[7][0]
        elif (science_datasetType == "DNB_Platform"):
            subhdflayer = hdflayer.GetSubDatasets()[8][0]
        elif (science_datasetType == "Land_Water_Mask"):
            subhdflayer = hdflayer.GetSubDatasets()[9][0]
        elif (science_datasetType == "NearNadir_Composite_Snow_Covered"):
            subhdflayer = hdflayer.GetSubDatasets()[10][0]
        elif (science_datasetType == "NearNadir_Composite_Snow_Covered_Num"):
            subhdflayer = hdflayer.GetSubDatasets()[11][0]
        elif (science_datasetType == "NearNadir_Composite_Snow_Covered_Quality"):
            subhdflayer = hdflayer.GetSubDatasets()[12][0]
        elif (science_datasetType == "NearNadir_Composite_Snow_Covered_Std"):
            subhdflayer = hdflayer.GetSubDatasets()[13][0]
        elif (science_datasetType == "NearNadir_Composite_Snow_Free"):
            subhdflayer = hdflayer.GetSubDatasets()[14][0]
        elif (science_datasetType == "NearNadir_Composite_Snow_Free_Num"):
            subhdflayer = hdflayer.GetSubDatasets()[15][0]
        elif (science_datasetType == "NearNadir_Composite_Snow_Free_Quality"):
            subhdflayer = hdflayer.GetSubDatasets()[16][0]
        elif (science_datasetType == "NearNadir_Composite_Snow_Free_Std"):
            subhdflayer = hdflayer.GetSubDatasets()[17][0]
        elif (science_datasetType == "OffNadir_Composite_Snow_Covered"):
            subhdflayer = hdflayer.GetSubDatasets()[18][0]
        elif (science_datasetType == "OffNadir_Composite_Snow_Covered_Num"):
            subhdflayer = hdflayer.GetSubDatasets()[19][0]
        elif (science_datasetType == "OffNadir_Composite_Snow_Covered_Quality"):
            subhdflayer = hdflayer.GetSubDatasets()[20][0]
        elif (science_datasetType == "OffNadir_Composite_Snow_Covered_Std"):
            subhdflayer = hdflayer.GetSubDatasets()[21][0]
        elif (science_datasetType == "OffNadir_Composite_Snow_Free"):
            subhdflayer = hdflayer.GetSubDatasets()[22][0]
        elif (science_datasetType == "OffNadir_Composite_Snow_Free_Num"):
            subhdflayer = hdflayer.GetSubDatasets()[23][0]
        elif (science_datasetType == "OffNadir_Composite_Snow_Free_Quality"):
            subhdflayer = hdflayer.GetSubDatasets()[24][0]
        elif (science_datasetType == "OffNadir_Composite_Snow_Free_Std"):
            subhdflayer = hdflayer.GetSubDatasets()[25][0]
        else:
            print("no this type....")
            return 0

        rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)
        # 子图层的名称
        outputName = subhdflayer[97:]
        outputNameFinal = outputName + rasterFilepre + fileExtension
        # print(outputNameFinal)

        # 构建文件输出路径
        outputFolder = output_dic
        outputRaster = outputFolder + outputNameFinal

        # print(rlayer.GetMetadata_Dict())
        # for key in rlayer.GetMetadata_Dict():
        #     print(key)
        #     print(rlayer.GetMetadata_Dict()[key])

        # 获取影像四至范围
        HorizontalTileNumber = int(rlayer.GetMetadata_Dict()["HorizontalTileNumber"])
        VerticalTileNumber = int(rlayer.GetMetadata_Dict()["VerticalTileNumber"])

        WestBoundCoord = (10 * HorizontalTileNumber) - 180
        NorthBoundCoord = 90 - (10 * VerticalTileNumber)
        EastBoundCoord = WestBoundCoord + 10
        SouthBoundCoord = NorthBoundCoord - 10

        EPSG = "-a_srs EPSG:4326"  # WGS84
        translateOptionText = EPSG + " -a_ullr " + str(WestBoundCoord) + " " + str(NorthBoundCoord) + " " + str(EastBoundCoord) + " " + str(SouthBoundCoord)
        translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))
        gdal.Translate(outputRaster, rlayer, options=translateoptions)
        # gdal.Warp(outputRaster, rlayer)
        print(outputNameFinal, "has finished...")

## 获取文件夹下所有深度的文件夹
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

if __name__=="__main__":
    gdal.AllRegister()  # 注册驱动

    # File_Type = "VNP46A2"
    # Science_DatasetType_List = ["QF_Cloud_Mask", "DNB_BRDF-Corrected_NTL", "Snow_Flag", "Mandatory_Quality_Flag"]
    File_Type = "VNP46A1"
    Science_DatasetType_List = ["Moon_Illumination_Fraction", "Solar_Zenith", "Sensor_Zenith"]

    work_dic = "G:\\postgraduate\\postgraduate_bishe\\" + File_Type + "_res\\"  # hdf文件存放的目录
    output_dic = "G:\\postgraduate\\postgraduate_bishe\\" + File_Type + "_res_tif\\"

    for SDS_Type in Science_DatasetType_List:
        output_dic1 = output_dic + SDS_Type + "\\"
        if not os.path.exists(output_dic1):
            os.makedirs(output_dic1)
        if (File_Type == "VNP46A2"):
            readVNP46A2(work_dic, output_dic1, SDS_Type)
        elif (File_Type == "VNP46A1"):
            readVNP46A1(work_dic, output_dic1, SDS_Type)
