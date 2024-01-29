import gdal
import glob
import os
# 计算经纬度坐标所对应的列号
import numpy as np
Events_Gadm_Level_List = {
    # "SYR_20220101_20230301": {"Adm00": ["TUR_SYR"]},
    # "SYR_20220101_20230301": {"Adm_urban": ["Adiyaman",
    #                                         "Aleppo",
    #                                         "Antakya",
    #                                         "Gaziantep",
    #                                         "Kahramanmaras",
    #                                         "Kirikhan",
    #                                         "Latakia",
    #                                         "Samandag"]},
    "SYR_20230301_20230501": {"Adm_urban": ["Adiyaman",
                                            "Aleppo",
                                            "Antakya",
                                            "Gaziantep",
                                            "Kahramanmaras",
                                            "Kirikhan",
                                            "Latakia",
                                            "Samandag"]},
}

LUCC_List = {
    # "LAS": "LAS_2020LC030_merge_image",
    # "USA": "USA_2020LC030_merge_image",
    # "IND": "IND_2020LC030_merge_image",
    "PRI": "PRI_2020LC030_merge_image",
}

def calTiffCol(lng,lat,GeoTransform):
    temp = GeoTransform[1]*GeoTransform[5] - GeoTransform[2]*GeoTransform[4]
    col = int((GeoTransform[5]*(lng-GeoTransform[0]) - GeoTransform[2]*(lat-GeoTransform[3])) / temp)
    return col

# 计算经纬度坐标所对应的行号
def calTiffRow(lng,lat,GeoTransform):
    temp = GeoTransform[1]*GeoTransform[5] - GeoTransform[2]*GeoTransform[4]
    row = int((GeoTransform[1]*(lat-GeoTransform[3]) - GeoTransform[4]*(lng-GeoTransform[0])) / temp)
    return row

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
    outband.SetNoDataValue(NaN_Value)
    outband.WriteArray(array)   #将数据写入获取的这个波段中（写入的数据只能是二维的）
    outRaster.FlushCache()
    del outRaster

# 生成每个文件的读取路径及文件名
def generateHDF5FilePath(folderPath):
    # 利用glob包，将inws下的所有tif文件读存放到rasters中
    rasters = glob.glob(os.path.join(folderPath, "*.tif"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][:-4]
        Name_List.append(Name)
    return rasters, Name_List

if __name__ == "__main__":
    File_Type = "VNP46A2_res"

    for key in Events_Gadm_Level_List:
        # 基于Country_Name_shorthand解析出国家缩写，数据收集的开始与结束时间
        eventID_startTime_endTime = key
        eventID_startTime_endTime_List = eventID_startTime_endTime.split("_")
        Start_Time_Str = eventID_startTime_endTime_List[1]
        End_Time_Str = eventID_startTime_endTime_List[2]
        Country_Code = eventID_startTime_endTime_List[0]

        Start_year = int(Start_Time_Str[:4])
        End_year = int(End_Time_Str[:4])

        for adm_type in sorted(Events_Gadm_Level_List[key]):

            for adm_name in Events_Gadm_Level_List[key][adm_type]:
                Extracted_Img_Dir = "G:\\postgraduate\\postgraduate_bishe\\" + File_Type + "_tif\\MaskFile_joint_clip_" + adm_name + "_noTranslation\\"
                LC_Img_Path = "G:\\postgraduate\\postgraduate_bishe\\LUCC\\TUR_SYR\\LUCC_Clip\\merge_" + adm_name + "_noTranslation.tif"
                print("ues", LC_Img_Path)

                Extracted_Img_Paths, Extracted_Img_Names = generateHDF5FilePath(Extracted_Img_Dir)

                Output_Img_Dir = "G:\\postgraduate\\postgraduate_bishe\\" + File_Type + "_tif\\MaskFile_joint_clip_" + adm_name + "_noTranslation_Constrained_By_LC_Larger50%\\"
                if not os.path.exists(Output_Img_Dir):
                    os.makedirs(Output_Img_Dir)
                for j in range(len(Extracted_Img_Paths)):
                    Extracted_Img_Path = Extracted_Img_Paths[j]
                    output_Result_Constrained_By_LC_Path = Output_Img_Dir + Extracted_Img_Names[j] + "_Constrained_By_LC_Larger50%.tif"

                    LC_Img_raster, LC_Img_geoTransform, LC_Img_proj, LC_Img_NaN_Value = read_tiff(LC_Img_Path)
                    Extracted_Img_raster, Extracted_Img_geoTransform, Extracted_Img_proj, Extracted_Img_NaN_Value = read_tiff(Extracted_Img_Path)

                    Extracted_Img_Start_lng = Extracted_Img_geoTransform[0]
                    Extracted_Img_Start_lat = Extracted_Img_geoTransform[3]
                    print(Extracted_Img_Path, "start...")
                    for row in range(len(Extracted_Img_raster)):
                        for col in range(len(Extracted_Img_raster[0])):
                            if (not np.isnan(Extracted_Img_raster[row][col])):
                                if (Extracted_Img_raster[row][col] == Extracted_Img_NaN_Value):
                                    continue
                                # Extracted_Img对应LC_Img的行列号
                                pixel_left_lng = Extracted_Img_Start_lng + (col * Extracted_Img_geoTransform[1])
                                pixel_right_lng = Extracted_Img_Start_lng + ((col + 1) * Extracted_Img_geoTransform[1])

                                pixel_top_lat = Extracted_Img_Start_lat + (row * Extracted_Img_geoTransform[5])
                                pixel_bottom_lat = Extracted_Img_Start_lat + ((row + 1) * Extracted_Img_geoTransform[5])

                                row_start_LC = calTiffRow(pixel_left_lng, pixel_top_lat, LC_Img_geoTransform)
                                col_start_LC = calTiffCol(pixel_left_lng, pixel_top_lat, LC_Img_geoTransform)

                                row_end_LC = calTiffRow(pixel_right_lng, pixel_bottom_lat, LC_Img_geoTransform)
                                col_end_LC = calTiffCol(pixel_right_lng, pixel_bottom_lat, LC_Img_geoTransform)

                                # 因为裁剪时像素存在错位，所以夜光影像与LUCC影像不一定能完全匹配上
                                if (row_start_LC < 0):
                                    row_start_LC = 0
                                if (col_start_LC < 0):
                                    col_start_LC = 0

                                area_array_LC = LC_Img_raster[row_start_LC:row_end_LC+1,col_start_LC:col_end_LC+1]

                                buildUp_80_rate = 0
                                for temp_r in range(len(area_array_LC)):
                                    for temp_c in range(len(area_array_LC[0])):
                                        if (area_array_LC[temp_r][temp_c] == 80):
                                            buildUp_80_rate += 1
                                if (buildUp_80_rate / (len(area_array_LC) * len(area_array_LC[0])) < 0.5):
                                    Extracted_Img_raster[row][col] = 0
                                # if (10 in area_array_LC or 20 in area_array_LC or
                                #     30 in area_array_LC or 40 in area_array_LC or
                                #     50 in area_array_LC or 60 in area_array_LC or
                                #     70 in area_array_LC or 90 in area_array_LC or
                                #     100 in area_array_LC or 71 in area_array_LC or
                                #     72 in area_array_LC or 73 in area_array_LC or
                                #     74 in area_array_LC):
                                #     Extracted_Img_raster[row][col] = 0


                    array2raster(output_Result_Constrained_By_LC_Path, Extracted_Img_raster, Extracted_Img_geoTransform,
                                 Extracted_Img_proj, Extracted_Img_NaN_Value)
                    print(output_Result_Constrained_By_LC_Path, "has benn finished...")



