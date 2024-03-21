from datetime import datetime
import glob
import os
import gdal
import math

Events_List = {
    # "TURSYR_20220101_20230301": ["h20v04", "h20v05", "h21v04", "h21v05", "h22v04", "h22v05"],
    # "TURSYR_20230301_20230501": ["h20v04", "h20v05", "h21v04", "h21v05", "h22v04", "h22v05"],
    "TURSYR_20230501_20240208": ["h20v04", "h20v05", "h21v04", "h21v05", "h22v04", "h22v05"],
}

#  Julian day to date
def jd_to_time(time):
    dt = datetime.strptime(time, '%Y%j').date()
    fmt = '%Y.%m.%d'
    return dt.strftime(fmt)

#  date to Julian day
def d_to_jd(time):
    fmt = '%Y.%m.%d'
    dt = datetime.strptime(time, fmt)
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday

# 用于给定起止时间，得到对应的年积日列表
def generateTimePeriod(start_tm, end_tm):
    TimePeriod_list = []

    jd_start_time = d_to_jd(start_tm)
    jd_end_time = d_to_jd(end_tm)

    # print(jd_start_time,jd_end_time)

    start_year = int(str(jd_start_time)[:4])
    end_year = int(str(jd_end_time)[:4])

    # 同一年的情况
    if (start_year == end_year):
        diff_time = jd_end_time - jd_start_time + 1
        for i in range(diff_time):
            TimePeriod_list.append(jd_start_time + i)
    # 不同年情况
    else:
        diff_year = end_year - start_year + 1
        for i in range(diff_year):
            temp_start_year = start_year + i
            if (i == 0):
                if (temp_start_year % 4 == 0):
                    temp_jd_end_time = int(str(temp_start_year) + "366")
                else:
                    temp_jd_end_time = int(str(temp_start_year) + "365")
                temp_diff_time = temp_jd_end_time - jd_start_time + 1
                for j in range(temp_diff_time):
                    TimePeriod_list.append(jd_start_time + j)
            elif (i == diff_year - 1):
                temp_jd_start_time = int(str(temp_start_year) + "001")
                temp_diff_time = jd_end_time - temp_jd_start_time + 1
                for j in range(temp_diff_time):
                    TimePeriod_list.append(temp_jd_start_time + j)
            else:
                temp_jd_start_time = int(str(temp_start_year) + "001")
                if (temp_start_year % 4 == 0):
                    temp_diff_time = 366
                else:
                    temp_diff_time = 365
                for j in range(temp_diff_time):
                    TimePeriod_list.append(temp_jd_start_time + j)

    return TimePeriod_list

# 生成每个文件的读取路径及文件名
def generateHDF5FilePath(folderPath):
    # 利用glob包，将inws下的所有tif文件读存放到rasters中
    rasters = glob.glob(os.path.join(folderPath, "*.tif"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][-36:-22]
        Name_List.append(Name)
    return rasters, Name_List

def generateMaskImgFilePath(folderPath):
    # 利用glob包，将inws下的所有tif文件读存放到rasters中
    rasters = glob.glob(os.path.join(folderPath, "*.tif"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][-23:-9]
        Name_List.append(Name)
    return rasters, Name_List

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

# 获取拼接后的四至边界
def GetJointExtent(Country_Image_File_Path_List):
    in_fn = Country_Image_File_Path_List[0]
    # 获取待镶嵌栅格的最大最小的坐标值(最外围轮廓的最大最小值)
    min_x, max_y, max_x, min_y = GetExtent(in_fn)
    for in_fn in Country_Image_File_Path_List[1:]:
        minx, maxy, maxx, miny = GetExtent(in_fn)
        min_x = min(min_x, minx)
        min_y = min(min_y, miny)
        max_x = max(max_x, maxx)
        max_y = max(max_y, maxy)
    return min_x, min_y, max_x, max_y

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

# !!!!! 处理DNB的代码
if __name__ == "__main__":
    File_Type = "VNP46A2_res_res"
    # 构建工作路径，并生成需要拼接的数据所在的文件夹
    work_dic = "G:\\postgraduate\\postgraduate_bishe"

    tif_dir = work_dic + "\\" + File_Type + "_tif"
    start_time = "2023.05.01"
    end_time = "2024.02.08"
    # 构建字典中的键，用于得到对应需要拼接的tiles；并构建读取NTL影像与掩码影像的文件夹路径，以及拼接后保存的文件夹路径
    Event_Index = "TURSYR_20230501_20240208"

    Tile_NTL_tif_path = tif_dir + "\\DNB_BRDF-Corrected_NTL\\"
    Tile_MaskImg_tif_path = tif_dir + "\\MaskFile\\"
    Tile_VZAImg_tif_path = work_dic + "\\VNP46A1_res_res_tif\\Sensor_Zenith\\"

    Output_NTL_dic = tif_dir + "\\DNB_BRDF-Corrected_NTL_joint\\"
    Output_MaskImg_dic = tif_dir + "\\MaskFile_joint\\"
    Output_VZAImg_dic = work_dic + "\\VNP46A1_res_res_tif\\Sensor_Zenith_joint\\"

    # 判断输出路径的文件夹是否存在，不存在则创建一个
    if not os.path.exists(Output_NTL_dic):
        os.makedirs(Output_NTL_dic)
    if not os.path.exists(Output_MaskImg_dic):
        os.makedirs(Output_MaskImg_dic)
    if not os.path.exists(Output_VZAImg_dic):
        os.makedirs(Output_VZAImg_dic)

    # 获取拼接数据的所有时间
    TimePeriod_list = generateTimePeriod(start_time, end_time)
    print(TimePeriod_list)
    # 获取拼接数据对应的tiles
    if (Event_Index in Events_List):
        Country_Tiles_List = Events_List[Event_Index]
        print(Country_Tiles_List)
        # 从文件夹中获取需要处理的所有文件路径，以及文件名
        NTL_Path_List, NTL_Name_List = generateHDF5FilePath(Tile_NTL_tif_path)
        MaskImg_Path_List, MaskImg_Name_List = generateMaskImgFilePath(Tile_MaskImg_tif_path)
        VZAImg_Path_List, VZAImg_Name_List = generateHDF5FilePath(Tile_VZAImg_tif_path)

        print(NTL_Path_List)
        print(NTL_Name_List)
        print(MaskImg_Path_List)
        print(MaskImg_Name_List)
        print(VZAImg_Path_List)
        print(VZAImg_Name_List)

        # 逐日期生成拼接影像
        for i in range(len(TimePeriod_list)):
            Joint_NTL_Images_Path_List = []
            Joint_MaskImg_Images_Path_List = []
            Joint_VZAImg_Images_Path_List = []
            # 获取一天内需要拼接的所有tile
            for j in range(len(Country_Tiles_List)):
                temp_NTL_Name = str(TimePeriod_list[i]) + "." + Country_Tiles_List[j]
                temp_MaskImg_Name = str(TimePeriod_list[i]) + "_" + Country_Tiles_List[j]
                temp_VZAImg_Name = str(TimePeriod_list[i]) + "." + Country_Tiles_List[j]
                if (temp_NTL_Name in NTL_Name_List):    # 一定要在列表里才能拼接，数据本身下载时存在缺失
                    index_i = NTL_Name_List.index(temp_NTL_Name)
                    tif_path = NTL_Path_List[index_i]
                    Joint_NTL_Images_Path_List.append(tif_path)
                if (temp_MaskImg_Name in MaskImg_Name_List):    # 一定要在列表里才能拼接，数据本身下载时存在缺失
                    index_i = MaskImg_Name_List.index(temp_MaskImg_Name)
                    tif_path = MaskImg_Path_List[index_i]
                    Joint_MaskImg_Images_Path_List.append(tif_path)
                if (temp_VZAImg_Name in VZAImg_Name_List):    # 一定要在列表里才能拼接，数据本身下载时存在缺失
                    index_i = VZAImg_Name_List.index(temp_VZAImg_Name)
                    tif_path = VZAImg_Path_List[index_i]
                    Joint_VZAImg_Images_Path_List.append(tif_path)
            # 这一天至少有一个tile需要拼接，如果都没有表明这一天该区域数据全部缺失
            if (len(Joint_NTL_Images_Path_List) != 0):
                # 获取待镶嵌栅格的最大最小的坐标值(最外围轮廓的最大最小值),MaskImg与NTL共用
                min_x, min_y, max_x, max_y = GetJointExtent(Joint_NTL_Images_Path_List)
                # min_x1, min_y1, max_x1, max_y1 = GetJointExtent(Joint_MaskImg_Images_Path_List)
                # 计算镶嵌后影像的行列号
                in_ds_NTL = gdal.Open(Joint_NTL_Images_Path_List[0])
                in_ds_MaskImg = gdal.Open(Joint_MaskImg_Images_Path_List[0])
                in_ds_VZAImg = gdal.Open(Joint_VZAImg_Images_Path_List[0])
                geotrans = list(in_ds_NTL.GetGeoTransform())
                width = geotrans[1]
                height = geotrans[5]
                columns = math.ceil((max_x - min_x) / width)  # 向上取整”， 即小数部分直接舍去，并向正数部分进1
                rows = math.ceil((max_y - min_y) / (-height))
                # 创建驱动，生成文件（MaskImg与NTL分开）
                in_band_NTL = in_ds_NTL.GetRasterBand(1)
                in_band_MaskImg = in_ds_MaskImg.GetRasterBand(1)
                in_band_VZAImg = in_ds_VZAImg.GetRasterBand(1)
                driver = gdal.GetDriverByName('GTiff')
                out_ds_NTL = driver.Create(
                    Output_NTL_dic + str(TimePeriod_list[i]) + "_joint_image.tif",
                    columns, rows, 1, in_band_NTL.DataType)
                out_ds_MaskImg = driver.Create(
                    Output_MaskImg_dic + str(TimePeriod_list[i]) + "_joint_image.tif",
                    columns, rows, 1, in_band_MaskImg.DataType)
                out_ds_VZAImg = driver.Create(
                    Output_VZAImg_dic + str(TimePeriod_list[i]) + "_joint_image.tif",
                    columns, rows, 1, in_band_VZAImg.DataType)
                out_ds_NTL.SetProjection(in_ds_NTL.GetProjection())
                out_ds_MaskImg.SetProjection(in_ds_NTL.GetProjection())
                out_ds_VZAImg.SetProjection(in_ds_NTL.GetProjection())
                geotrans[0] = min_x
                geotrans[3] = max_y
                out_ds_NTL.SetGeoTransform(geotrans)
                out_ds_MaskImg.SetGeoTransform(geotrans)
                out_ds_VZAImg.SetGeoTransform(geotrans)
                out_band_NTL = out_ds_NTL.GetRasterBand(1)
                out_band_MaskImg = out_ds_MaskImg.GetRasterBand(1)
                out_band_VZAImg = out_ds_VZAImg.GetRasterBand(1)

                # 定义仿射逆变换
                inv_geotrans = gdal.InvGeoTransform(geotrans)
                # 开始逐渐写入
                for ppp in range(len(Joint_NTL_Images_Path_List)):
                    in_ds_NTL = gdal.Open(Joint_NTL_Images_Path_List[ppp])
                    in_ds_MaskImg = gdal.Open(Joint_MaskImg_Images_Path_List[ppp])
                    in_ds_VZAImg = gdal.Open(Joint_VZAImg_Images_Path_List[ppp])

                    in_gt_NTL = in_ds_NTL.GetGeoTransform()
                    in_gt_MaskImg = in_ds_MaskImg.GetGeoTransform()
                    in_gt_VZAImg = in_ds_VZAImg.GetGeoTransform()

                    # 仿射逆变换
                    offset = gdal.ApplyGeoTransform(inv_geotrans, in_gt_NTL[0], in_gt_NTL[3])
                    x, y = map(int, offset)
                    data_NTL = in_ds_NTL.GetRasterBand(1).ReadAsArray()
                    data_MaskImg = in_ds_MaskImg.GetRasterBand(1).ReadAsArray()
                    data_VZAImg = in_ds_VZAImg.GetRasterBand(1).ReadAsArray()
                    out_band_NTL.WriteArray(data_NTL, x, y)  # x，y是开始写入时左上角像元行列号
                    out_band_MaskImg.WriteArray(data_MaskImg, x, y)  # x，y是开始写入时左上角像元行列号
                    out_band_VZAImg.WriteArray(data_VZAImg, x, y)  # x，y是开始写入时左上角像元行列号
                    # 将缓存写入磁盘
                    out_band_NTL.FlushCache()
                    out_band_MaskImg.FlushCache()
                    out_band_VZAImg.FlushCache()
                del in_ds_NTL, in_ds_MaskImg, in_ds_VZAImg, out_band_NTL, out_band_MaskImg, out_band_VZAImg, out_ds_NTL, out_ds_MaskImg, out_ds_VZAImg
                print(str(TimePeriod_list[i]), "NTL, MaskImg and VZAImg has joint!")

