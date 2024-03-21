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
    # "TUR_20220101_20230301": {"Adm0": ["TUR"]},
    # "SYR_20220101_20230301": {"Adm0": ["SYR"]},

    # "SYR_20220101_20230301": {"Adm00": ["TUR_SYR"]},
    # "SYR_20220101_20230301": {"Adm_urban": ["Adiyaman",
    #                                         "Aleppo",
    #                                         "Antakya",
    #                                         "Gaziantep",
    #                                         "Kahramanmaras",
    #                                         "Kirikhan",
    #                                         "Latakia",
    #                                         "Samandag"]},
    # "SYR_20230301_20230501": {"Adm00": ["TUR_SYR"]},
    # "SYR_20230301_20230501": {"Adm_urban": ["Adiyaman",
    #                                         "Aleppo",
    #                                         "Antakya",
    #                                         "Gaziantep",
    #                                         "Kahramanmaras",
    #                                         "Kirikhan",
    #                                         "Latakia",
    #                                         "Samandag"]},
    "TURSYR_20230501_20240208": {"Adm_urban": ["Adiyaman",
                                            "Antakya",
                                            "Kahramanmaras",
                                            "Kirikhan",
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

# !!!!! 处理掩码的代码
if __name__ == "__main__":
    File_Type = "VNP46A2_res_res"

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
                Joint_Tif_MaskImg_Path = "G:\\postgraduate\\postgraduate_bishe\\" + File_Type + "_tif\\" + "MaskFile_joint\\"
                Joint_Tif_NTL_Path = "G:\\postgraduate\\postgraduate_bishe\\" + File_Type + "_tif\\" + "DNB_BRDF-Corrected_NTL_joint\\"
                Joint_Tif_VZAImg_Path = "G:\\postgraduate\\postgraduate_bishe\\VNP46A1_res_res_tif\\Sensor_Zenith_joint\\"

                Output_Clip_Tif_MaskImg_Dic = "G:\\postgraduate\\postgraduate_bishe\\" + File_Type + "_tif\\" + "MaskFile_joint_clip_" + Gadm_Name + "_noTranslation\\"
                Output_Clip_Tif_NTL_Dic = "G:\\postgraduate\\postgraduate_bishe\\" + File_Type + "_tif\\" + "DNB_BRDF-Corrected_NTL_joint_clip_" + Gadm_Name + "_noTranslation\\"
                Output_Clip_Tif_VZAImg_Dic = "G:\\postgraduate\\postgraduate_bishe\\VNP46A1_res_res_tif\\Sensor_Zenith_joint_clip_" + Gadm_Name + "_noTranslation\\"

                mask_dic_new = ""
                if (adm_type == "Adm_urban"):
                    mask_dic_new = "G:\\postgraduate\\postgraduate_bishe\\boundry\\" + Gadm_Name + ".shp"
                if (adm_type == "Adm00"):
                    mask_dic_new = "G:\\postgraduate\\postgraduate_bishe\\boundry\\" + Gadm_Name + ".shp"
                if (adm_type == "Adm0"):
                    mask_dic_new = "G:\\postgraduate\\postgraduate_bishe\\boundry\\gadm41_" + Country_Code + "_shp\\gadm41_" + Gadm_Name + "_0.shp"
                if (adm_type == "Adm1"):
                    mask_dic_new = "D:\\VZA_Article\\data\\gadm\\gadm_" + Country_Code + "\\adm1\\" + Gadm_Name + ".shp"
                elif (adm_type == "Adm2"):
                    mask_dic_new = "D:\\VZA_Article\\data\\gadm\\gadm_" + Country_Code + "\\adm2\\" + Gadm_Name + ".shp"
                elif (adm_type == "Adm3"):
                    mask_dic_new = "D:\\VZA_Article\\data\\gadm\\gadm_" + Country_Code + "\\adm3\\" + Gadm_Name + ".shp"

                # 判断输出路径的文件夹是否存在，不存在则创建一个
                if not os.path.exists(Output_Clip_Tif_MaskImg_Dic.decode('utf-8')):
                    os.makedirs(Output_Clip_Tif_MaskImg_Dic.decode('utf-8'))
                if not os.path.exists(Output_Clip_Tif_NTL_Dic.decode('utf-8')):
                    os.makedirs(Output_Clip_Tif_NTL_Dic.decode('utf-8'))
                if not os.path.exists(Output_Clip_Tif_VZAImg_Dic.decode('utf-8')):
                    os.makedirs(Output_Clip_Tif_VZAImg_Dic.decode('utf-8'))

                # 从文件夹中获取需要处理的所有文件路径，以及文件名
                H5Files_MaskImg_Path_List, H5Files_MaskImg_Name_List = generateHDF5FilePath(Joint_Tif_MaskImg_Path)
                H5Files_NTL_Path_List, H5Files_NTL_Name_List = generateHDF5FilePath(Joint_Tif_NTL_Path)
                H5Files_VZAImg_Path_List, H5Files_VZAImg_Name_List = generateHDF5FilePath(Joint_Tif_VZAImg_Path)

                # 逐文件遍历
                for i in range(len(H5Files_MaskImg_Path_List)):
                    # 需要判断一下矢量边界和栅格边界之间的关系
                    # 导入栅格shp文件
                    r = shapefile.Reader(mask_dic_new.decode('utf-8'))
                    min_x_shp, min_y_shp, max_x_shp, max_y_shp = r.bbox  # minX、maxY为左上角坐标；另一个为右下角坐标
                    min_x_tif, max_y_tif, max_x_tif, min_y_tif = GetExtent(H5Files_MaskImg_Path_List[i])
                    if (((min_x_tif <= min_x_shp <= max_x_tif) or (min_x_tif <= max_x_shp <= max_x_tif)) and (
                            (min_y_tif <= min_y_shp <= max_y_tif) or (min_y_tif <= max_y_shp <= max_y_tif))):
                        # 输出文件夹路径
                        output_work_dic_MaskImg = Output_Clip_Tif_MaskImg_Dic
                        output_work_dic_NTL = Output_Clip_Tif_NTL_Dic
                        output_work_dic_VZAImg = Output_Clip_Tif_VZAImg_Dic
                        # 输入影像文件路径
                        ras_MaskImg = H5Files_MaskImg_Path_List[i]
                        ras_NTL = H5Files_NTL_Path_List[i]
                        ras_VZAImg = H5Files_VZAImg_Path_List[i]
                        # 输出影像文件路径
                        outname_MaskImg = os.path.join(output_work_dic_MaskImg, str(H5Files_MaskImg_Name_List[
                                                                                        i]) + "_" + Gadm_Name + "_Clp.tif")  # 指定输出文件的命名方式（以被裁剪文件名+_clip.tif命名）
                        outname_NTL = os.path.join(output_work_dic_NTL, str(H5Files_NTL_Name_List[
                                                                                i]) + "_" + Gadm_Name + "_Clp.tif")  # 指定输出文件的命名方式（以被裁剪文件名+_clip.tif命名）
                        outname_VZAImg = os.path.join(output_work_dic_VZAImg, str(H5Files_VZAImg_Name_List[
                                                                                        i]) + "_" + Gadm_Name + "_Clp.tif")  # 指定输出文件的命名方式（以被裁剪文件名+_clip.tif命名）
                        # print (outname)
                        # 掩膜提取
                        # print (ras_MaskImg)
                        # print (mask_dic_new)
                        # 栅格捕捉，防止剪切平移
                        tempEnvironment0 = arcpy.env.snapRaster
                        arcpy.env.snapRaster = ras_MaskImg
                        out_extract_MaskImg = arcpy.sa.ExtractByMask(ras_MaskImg, mask_dic_new)  # 执行按掩模提取操作
                        out_extract_MaskImg.save(outname_MaskImg)  # 保存数据
                        arcpy.env.snapRaster = tempEnvironment0
                        print (outname_MaskImg + " finished")

                        # 栅格捕捉，防止剪切平移
                        tempEnvironment0 = arcpy.env.snapRaster
                        arcpy.env.snapRaster = ras_NTL
                        out_extract_NTL = arcpy.sa.ExtractByMask(ras_NTL, mask_dic_new)  # 执行按掩模提取操作
                        out_extract_NTL.save(outname_NTL)  # 保存数据
                        arcpy.env.snapRaster = tempEnvironment0
                        print (outname_NTL + " finished")

                        # 栅格捕捉，防止剪切平移
                        tempEnvironment0 = arcpy.env.snapRaster
                        arcpy.env.snapRaster = ras_VZAImg
                        out_extract_VZAImg = arcpy.sa.ExtractByMask(ras_VZAImg, mask_dic_new)  # 执行按掩模提取操作
                        out_extract_VZAImg.save(outname_VZAImg)  # 保存数据
                        arcpy.env.snapRaster = tempEnvironment0
                        print (outname_VZAImg + " finished")



