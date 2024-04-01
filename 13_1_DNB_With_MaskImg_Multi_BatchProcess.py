#/usr/bin/env python
# -*- coding: UTF-8 -*-

import gdal
import glob
import os
import numpy as np

Disaster_Province_1Level_List = {
    "TUR_SYR_20220902_20240208":["Adiyaman", "Antakya", "Kahramanmaras", "Kirikhan", "Samandag"],
}

# 读取tiff文件
def read_tiff(filename):
    datasets=gdal.Open(filename)  # 读取文件
    row=datasets.RasterXSize    # 获取数据的宽
    col=datasets.RasterYSize    # 获取数据的高
    band=datasets.RasterCount   # 获取数据的波段数

    geoTransform = datasets.GetGeoTransform()   # 仿射矩阵
    proj = datasets.GetProjection()     # 获取投影信息
    dt = datasets.GetRasterBand(1)  # 读取i+1波段信息（读取时从1开始）
    NaN_Value = dt.GetNoDataValue()  # 得到影像中nodata的数值
    data = dt.ReadAsArray(0,0,row,col) # Getting data from 0 rows and 0 columns
    del datasets
    return data,geoTransform,proj, NaN_Value

# 写入tiff文件
def array2raster(outpath,array,geoTransform,proj,NaN_Value):
    if 'int8' in array.dtype.name:  # 判断栅格数据的数据类型
        datatype = gdal.GDT_Byte
    elif 'int16' in array.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    # datatype = gdal.GDT_UInt16

    cols=array.shape[1]
    rows=array.shape[0]
    driver=gdal.GetDriverByName('Gtiff')
    outRaster=driver.Create(outpath,cols,rows,1,datatype)
    outRaster.SetGeoTransform(geoTransform)#参数2,6为水平垂直分辨率，参数3,5表示图片是指北的
    outRaster.SetProjection(proj)#将几何对象的数据导出为wkt格式
    outband=outRaster.GetRasterBand(1)  #获取已经创建好的一个波段
    outband.SetNoDataValue(np.nan)
    outband.WriteArray(array)   #将数据写入获取的这个波段中（写入的数据只能是二维的）
    outRaster.FlushCache()
    del outRaster

# 生成每个文件的读取路径及文件名
def generateTIFFilePath(folderPath):
    # 利用glob包，将inws下的所有tif文件读存放到rasters中
    rasters = glob.glob(os.path.join(folderPath, "*.tif"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][:-4]
        Name_List.append(Name)
    return rasters, Name_List

if __name__ == "__main__":
    for key in sorted(Disaster_Province_1Level_List):
        for each_province in Disaster_Province_1Level_List[key]:
            Province_Name_shorthand = each_province
            Country_Name_shorthand = key

            print(Province_Name_shorthand, Country_Name_shorthand)

            # 基于Country_Name_shorthand解析出国家缩写，数据收集的开始与结束时间
            Country_Name_shorthand_List = Country_Name_shorthand.split("_")
            Country_Code = Country_Name_shorthand_List[0]
            Start_Time_Str = Country_Name_shorthand_List[1]
            End_Time_Str = Country_Name_shorthand_List[2]

            # 构建需要读取的影像与掩码文件夹，以及基于掩码文件生成的夜光影像文件保存路径
            DNB_Path = "G:\\postgraduate\\postgraduate_bishe\\VNP46A2_tif\\DNB_BRDF-Corrected_NTL_joint_clip_" + Province_Name_shorthand + "_noTranslation\\"
            MaskImg_Path = "G:\\postgraduate\\postgraduate_bishe\\VNP46A2_tif\\MaskFile_joint_clip_" + Province_Name_shorthand + "_noTranslation\\"
            outputFile_dic =  "G:\\postgraduate\\postgraduate_bishe\\VNP46A2_tif\\DNB_BRDF-Corrected_NTL_joint_clip_" + Province_Name_shorthand + "_Masked\\"

            # 判断输出路径的文件夹是否存在，不存在则创建一个
            if not os.path.exists(outputFile_dic):
                os.makedirs(outputFile_dic)

            # 从文件夹中获取需要处理的所有文件路径，以及文件名
            DNB_Files, DNB_Names = generateTIFFilePath(DNB_Path)
            MaskImg_Files, MaskImg_Names = generateTIFFilePath(MaskImg_Path)

            print(DNB_Files)
            print(DNB_Names)
            print(MaskImg_Files)
            print(MaskImg_Names)

            # 逐文件遍历处理
            for i in range(len(DNB_Files)):
                # 读取同一天影像对应的NTL与掩码影像
                raster_DNB, geoTransform_DNB, proj_DNB, NaN_Value_DNB = read_tiff(DNB_Files[i])
                raster_MaskImg, geoTransform_MaskImg, proj_MaskImg, NaN_Value_MaskImg = read_tiff(MaskImg_Files[i])
                raster_MaskImg = raster_MaskImg.astype(float)   # 因为数据之后要保存在该数组中，需要将原来的uint8改成float类型

                # 逐像素遍历
                for row in range(len(raster_DNB)):
                    for col in range(len(raster_DNB[0])):
                        # if (raster_MaskImg[row][col] == 1):
                        # 掩码像素为1，即为有效像素，并且保证NTL值也是有效的
                        if (raster_MaskImg[row][col] == 1 and raster_DNB[row][col] < 65535):
                            raster_MaskImg[row][col] = raster_DNB[row][col]
                            # print(raster_MaskImg[row][col])
                        # 这里包含了影像裁剪后的范围之外的nodata像素以及范围内的无效像素，均设置为np.nan
                        # （如果后期要区分这两类，可用NaN_Value做一个判断，为这个像素赋予一个独特的新值）
                        else:
                            # raster_MaskImg[row][col] = NaN_Value_DNB
                            raster_MaskImg[row][col] = np.nan

                # ImgResult_Array = raster_DNB * raster_MaskImg

                array2raster(outputFile_dic + MaskImg_Names[i] + "_DNB_Masked.tif", raster_MaskImg, geoTransform_DNB, proj_DNB, NaN_Value_DNB)
                print(MaskImg_Names[i] + "_DNB_Masked.tif File has been Generated...")


### arcpy这个代码有问题，因为掩码有0的部分，如果掩码是0，像素是65535的情况，先乘完就变为0了，但其实应该标记为nodata，无效数据
### 确实存在掩码标记为1的，但是DNB值还有65535
# import glob
# import os
# import arcpy
#
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
#
# print sys.getdefaultencoding()
# # sys.setdefaultencoding('utf-8')
#
# arcpy.CheckOutExtension('Spatial')
#
# # 生成每个文件的读取路径及文件名
# def generateTIFFilePath(folderPath):
#     # 利用glob包，将inws下的所有tif文件读存放到rasters中
#     rasters = glob.glob(os.path.join(folderPath, "*.tif"))
#     Name_List = []
#     for i in range(len(rasters)):
#         Name = rasters[i].split("\\")[-1][:-4]
#         Name_List.append(Name)
#     return rasters, Name_List
#
# if __name__ == "__main__":
#     DNB_Path = "G:\\disaster_research_OECD_country_data\\CHL\\20150616_20151016_Provinces_tif\\DNB_BRDF-Corrected_NTL_joint_clip\\"
#     MaskImg_Path = "G:\\disaster_research_OECD_country_data\\CHL\\20150616_20151016_Provinces_tif\\MaskFile_joint_clip\\"
#     outputFile_dic = "G:\\disaster_research_OECD_country_data\\CHL\\20150616_20151016_Provinces_tif\\DNB_BRDF-Corrected_NTL_joint_clip_Masked_Arcpy\\"
#
#
#     # 判断输出路径的文件夹是否存在，不存在则创建一个
#     if not os.path.exists(outputFile_dic):
#         os.makedirs(outputFile_dic)
#
#     DNB_Files, DNB_Names = generateTIFFilePath(DNB_Path)
#     MaskImg_Files, MaskImg_Names = generateTIFFilePath(MaskImg_Path)
#
#     print(DNB_Files)
#     print(MaskImg_Files)
#
#     for i in range(len(DNB_Files)):
#         rasterDNB = arcpy.Raster(DNB_Files[i])
#         rasterMaskImg = arcpy.Raster(MaskImg_Files[i])
#         # print (rasterDNB)
#         # print (rasterMaskImg)
#         raster_MaskedDNB = rasterDNB * rasterMaskImg
#         outSetNull = arcpy.sa.SetNull(raster_MaskedDNB, raster_MaskedDNB, "VALUE = 65535")  #  Or VALUE = 0
#         outSetNull.save(outputFile_dic + MaskImg_Names[i] + "_DNB_Masked.tif")
#         print(MaskImg_Names[i] + "_DNB_Masked.tif File has been Generated...")