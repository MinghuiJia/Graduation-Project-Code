#/usr/bin/env python
# -*- coding: UTF-8 -*-
import arcpy
import glob
import os
import shapefile
import gdal
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

Events_Gadm_Level_List = {
    # "SYR_20220101_20230301": {"Adm00": ["TUR_SYR"]},
    "SYR_20220101_20230301": {"Adm_urban": ["Adiyaman",
                                            "Aleppo",
                                            "Antakya",
                                            "Gaziantep",
                                            "Kahramanmaras",
                                            "Kirikhan",
                                            "Latakia",
                                            "Samandag"]},
}

#获取影像的左上角和右下角坐标
def GetExtent(in_fn):
    ds=gdal.Open(in_fn)
    geotrans=list(ds.GetGeoTransform())
    xsize=ds.RasterXSize
    ysize=ds.RasterYSize
    min_x=geotrans[0]
    max_y=geotrans[3]
    max_x=geotrans[0]+xsize*geotrans[1]
    min_y=geotrans[3]+ysize*geotrans[5]
    ds=None
    return min_x,max_y,max_x,min_y

# 生成每个文件的读取路径及文件名
def generateHDF5FilePath(folderPath):
    # 利用glob包，将inws下的所有tif文件读存放到rasters中
    rasters = glob.glob(os.path.join(folderPath, "*.tif"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][:-4]
        Name_List.append(Name)
    return rasters, Name_List

arcpy.CheckOutExtension('Spatial')

# aaa = shapefile.Reader("G:\\disaster_research_OECD_country_data\\PRI\\20170901_20180401_tif\\Country_Shp\\gadm36_PRI_0.shp")

# !!!!! 处理掩码的代码
if __name__ == "__main__":
    File_Type = "VNP46A2"

    for key in sorted (Events_Gadm_Level_List):
        for adm_type in sorted(Events_Gadm_Level_List[key]):
            for adm_shp_name in Events_Gadm_Level_List[key][adm_type]:
                Gadm_Name = adm_shp_name
                eventID_startTime_endTime = key
                print(Gadm_Name.decode('utf-8'), eventID_startTime_endTime)

                # 基于Country_Name_shorthand解析出国家缩写，数据收集的开始与结束时间
                eventID_startTime_endTime_List = eventID_startTime_endTime.split("_")
                Start_Time_Str = eventID_startTime_endTime_List[1]
                End_Time_Str = eventID_startTime_endTime_List[2]
                Country_Code = eventID_startTime_endTime_List[0]

                # 构建需要读取的夜光影像与掩码影像文件夹，以及夜光影像与掩码影像对应保存的文件夹路径，同时构建用于裁剪参考的gadm文件路径
                Joint_Tif_LUCCImg_Dir = "G:\\postgraduate\\postgraduate_bishe\\LUCC\\TUR_SYR\\merge\\"
                Joint_Tif_LUCCImg_Path,Joint_Tif_LUCCImg_Name = generateHDF5FilePath(Joint_Tif_LUCCImg_Dir)
                Output_Clip_Tif_Dir = "G:\\postgraduate\\postgraduate_bishe\\LUCC\\TUR_SYR\\LUCC_Clip\\"
                if not os.path.exists(Output_Clip_Tif_Dir.decode('utf-8')):
                    os.makedirs(Output_Clip_Tif_Dir.decode('utf-8'))
                for i in range(len(Joint_Tif_LUCCImg_Path)):

                    Output_Clip_Tif_Path = Output_Clip_Tif_Dir + Joint_Tif_LUCCImg_Name[i] + "_" + Gadm_Name + "_noTranslation.tif"
                    mask_dic_new = ""
                    if (adm_type == "Adm_urban"):
                        mask_dic_new = "G:\\postgraduate\\postgraduate_bishe\\boundry\\" + Gadm_Name + ".shp"
                    if (adm_type == "Adm00"):
                        mask_dic_new = "G:\\postgraduate\\postgraduate_bishe\\boundry\\" + Gadm_Name + ".shp"
                    if (adm_type == "Adm1"):
                        mask_dic_new = "D:\\VZA_Article\\data\\gadm\\gadm_" + Country_Code + "\\adm1\\" + Gadm_Name + ".shp"
                    elif (adm_type == "Adm2"):
                        mask_dic_new = "D:\\VZA_Article\\data\\gadm\\gadm_" + Country_Code + "\\adm2\\" + Gadm_Name + ".shp"
                    elif (adm_type == "Adm3"):
                        mask_dic_new = "D:\\VZA_Article\\data\\gadm\\gadm_" + Country_Code + "\\adm3\\" + Gadm_Name + ".shp"

                    r = shapefile.Reader(mask_dic_new.decode('utf-8'))
                    min_x_shp, min_y_shp, max_x_shp, max_y_shp = r.bbox  # minX、maxY为左上角坐标；另一个为右下角坐标
                    min_x_tif, max_y_tif, max_x_tif, min_y_tif = GetExtent(Joint_Tif_LUCCImg_Path[i])
                    if (((min_x_tif <= min_x_shp <= max_x_tif) or (min_x_tif <= max_x_shp <= max_x_tif)) and (
                            (min_y_tif <= min_y_shp <= max_y_tif) or (min_y_tif <= max_y_shp <= max_y_tif))):

                        # 输入影像文件路径
                        ras_LUCCImg = Joint_Tif_LUCCImg_Path[i]
                        # 输出影像文件路径
                        outname_LUCC = Output_Clip_Tif_Path # 指定输出文件的命名方式（以被裁剪文件名+_clip.tif命名）

                        # 栅格捕捉，防止剪切平移
                        tempEnvironment0 = arcpy.env.snapRaster
                        arcpy.env.snapRaster = ras_LUCCImg
                        out_extract_MaskImg = arcpy.sa.ExtractByMask(ras_LUCCImg, mask_dic_new)  # 执行按掩模提取操作
                        out_extract_MaskImg.save(outname_LUCC)  # 保存数据
                        arcpy.env.snapRaster = tempEnvironment0
                        print (outname_LUCC + " finished")



