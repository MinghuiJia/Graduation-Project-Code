import glob
import os
import gdal
from datetime import datetime
import scipy.stats as stats

# 生成每个文件的读取路径及文件名
import numpy as np

Disaster_Province_1Level_List = {
    "TUR_SYR_20220902_20240208":["Adiyaman", "Antakya", "Kahramanmaras", "Kirikhan", "Samandag"],
}

Disaster_Occur_Time_List = {
    "TUR_SYR_20220902_20240208":["20230206", 1, "EQ"],
}

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

# 根据文件夹路径生成文件夹内部tif后缀的所有文件路径以及文件名
def generateHDF5FilePath(folderPath):
    # 利用glob包，将inws下的所有tif文件读存放到rasters中
    rasters = glob.glob(os.path.join(folderPath, "*.tif"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][:-4]
        Name_List.append(Name)
    return rasters, Name_List

#  Julian day to date
def jd_to_time(time):
    dt = datetime.strptime(time, '%Y%j').date()
    fmt = '%Y%m%d'
    return dt.strftime(fmt)

#  date to Julian day
def d_to_jd(time):
    fmt = '%Y%m%d'
    dt = datetime.strptime(time, fmt)
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday

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

# 生成灾前均值影像与灾后5天均值影像
def generateDisasterPreAndPostMeanImg(NTL_File_Path, NTL_File_Name, Disaster_Occur_Time):
    geoTransform_reference, proj_reference, NaN_Value_reference = 0, 0, 0  # 第一张影像的基本信息作为参照
    pre_disaster_img_array = []
    post_disaster_img_array = []
    pre_disaster_img_array_count = []
    post_disaster_img_array_count = []

    # 需要针对灾后+5天得到的DOY进行分情况（如果是年末需要跨年的，+5之后大于366需要分情况）
    Disaster_Occur_DOY = d_to_jd(Disaster_Occur_Time)  # 受灾开始的YYYYMMDD转换成DOY形式
    Post_Disaster_DOY = int(Disaster_Occur_DOY) + 90
    Pre_Disaster_DOY = int(Disaster_Occur_DOY) - 10
    Year = int(str(Post_Disaster_DOY)[:4])
    Day = int(str(Post_Disaster_DOY)[4:])
    # 闰年
    if ((Year % 400 == 0) or (Year % 4 == 0 and Year % 100 != 0)):
        if (Day > 366):
            diff = str(Day - 366)
            if (len(diff) < 3):
                for k in range(3 - len(diff)):
                    diff = "0" + diff
            Post_Disaster_DOY = int(str(Year + 1) + diff)
    # 平年
    else:
        if (Day > 365):
            diff = str(Day - 365)
            if (len(diff) < 3):
                for k in range(3 - len(diff)):
                    diff = "0" + diff
            Post_Disaster_DOY = int(str(Year + 1) + diff)
    print("Disaster_Occur_Time:",Disaster_Occur_Time,"Disaster_Occur_DOY:",Disaster_Occur_DOY,"Post_Disaster_DOY:",Post_Disaster_DOY)

    # 逐文件遍历
    for i in range(len(NTL_File_Path)):
        # 从文件名中解析影像的时间
        Name_List = NTL_File_Name[i].split("_")
        DOY = Name_List[0]
        data_NTL, geoTransform_NTL, proj_NTL, NaN_Value_NTL = read_tiff(NTL_File_Path[i])   # 读取NTL影像
        # 将第一幅影像作为基准参考，因为第一幅没有缺失错位等情况
        if (i == 0):
            # 因为没有时间段内第一天就缺失的情况，所以将第一天的数据作为标准，需要得到左上角坐标作为参考
            Img_row, Img_col = data_NTL.shape
            pre_disaster_img_array = np.zeros((Img_row, Img_col))
            pre_disaster_img_array_count = np.zeros((Img_row, Img_col))
            post_disaster_img_array = np.zeros((Img_row, Img_col))
            post_disaster_img_array_count = np.zeros((Img_row, Img_col))
            geoTransform_reference = geoTransform_NTL
            proj_reference = proj_NTL
            NaN_Value_reference = NaN_Value_NTL
        # 统计灾前数据
        # if ((int(Disaster_Occur_DOY) - 30) > int(DOY)):
        #     continue
        # if ((int(Disaster_Occur_DOY) - 30) <= int(DOY) < int(Disaster_Occur_DOY)):
        if (Pre_Disaster_DOY <= int(DOY) < int(Disaster_Occur_DOY)):
            # print("pre disaster:",NTL_File_Path[i])
            row_start = calTiffRow(geoTransform_NTL[0], geoTransform_NTL[3], geoTransform_reference)
            col_start = calTiffCol(geoTransform_NTL[0], geoTransform_NTL[3], geoTransform_reference)
            # print("lng", geoTransform_NTL[0], "lat", geoTransform_NTL[3])
            # print("ref_lng", geoTransform_reference[0], "ref_lat", geoTransform_reference[3])
            # print("row_start",row_start,"col_start",col_start)
            for row in range(len(data_NTL)):
                for col in range(len(data_NTL[0])):
                    # 只统计有效数据计算均值, 这里需要做一个高值判断，如果出现异常高值的数据，不应该用于求均值
                    if (not np.isnan(data_NTL[row][col]) and data_NTL[row][col] != NaN_Value_NTL and data_NTL[row][col] < 5000):
                        pre_disaster_img_array[row+row_start][col+col_start] += data_NTL[row][col]
                        pre_disaster_img_array_count[row+row_start][col+col_start] += 1
            print(NTL_File_Name[i], "has finished...")
        # 统计灾后5天数据
        elif (int(Disaster_Occur_DOY) <= int(DOY) < Post_Disaster_DOY):
            # print("post disaster:", NTL_File_Path[i])
            row_start = calTiffRow(geoTransform_NTL[0], geoTransform_NTL[3], geoTransform_reference)
            col_start = calTiffCol(geoTransform_NTL[0], geoTransform_NTL[3], geoTransform_reference)
            # print("lng", geoTransform_NTL[0], "lat", geoTransform_NTL[3])
            # print("ref_lng", geoTransform_reference[0], "ref_lat", geoTransform_reference[3])
            # print("row_start", row_start, "col_start", col_start)
            for row in range(len(data_NTL)):
                for col in range(len(data_NTL[0])):
                    # 只统计有效数据计算均值
                    if (not np.isnan(data_NTL[row][col]) and data_NTL[row][col] != NaN_Value_NTL and data_NTL[row][col] < 5000):
                        post_disaster_img_array[row+row_start][col+col_start] += data_NTL[row][col]
                        post_disaster_img_array_count[row+row_start][col+col_start] += 1
            print(NTL_File_Name[i], "has finished...")

    # 逐像素计算均值
    # np.divide中如果不设置out参数，即Note that if an uninitialized out array is created via the default out=None
    # where条件为False的地方将保持未初始化状态
    pre_disaster_img_array = np.divide(pre_disaster_img_array, pre_disaster_img_array_count, out=np.zeros_like(pre_disaster_img_array), where=pre_disaster_img_array_count!=0)
    post_disaster_img_array = np.divide(post_disaster_img_array, post_disaster_img_array_count, out=np.zeros_like(post_disaster_img_array), where=post_disaster_img_array_count!=0)
    # 无有效数据的像素经过计算后为0，所以将所以0像素设为np.nan
    pre_disaster_img_array[pre_disaster_img_array_count == 0] = np.nan      # 因为可能本身就有0的情况，所以要根据count来判断
    post_disaster_img_array[post_disaster_img_array_count == 0] = np.nan
    ## 另一种复杂方式逐像素计算均值，比较慢
    # for pp in range(len(pre_disaster_img_array)):
    #     for qq in range(len(pre_disaster_img_array[0])):
    #         if (pre_disaster_img_array_count[pp][qq] == 0):
    #             pre_disaster_img_array[pp][qq] = np.nan
    #         else:
    #             pre_disaster_img_array[pp][qq] = pre_disaster_img_array[pp][qq] / pre_disaster_img_array_count[pp][qq]
    #
    # for pp in range(len(post_disaster_img_array)):
    #     for qq in range(len(post_disaster_img_array[0])):
    #         if (post_disaster_img_array_count[pp][qq] == 0):
    #             post_disaster_img_array[pp][qq] = np.nan
    #         else:
    #             post_disaster_img_array[pp][qq] = post_disaster_img_array[pp][qq] / post_disaster_img_array_count[pp][qq]

    return pre_disaster_img_array, post_disaster_img_array, geoTransform_reference, proj_reference, NaN_Value_reference

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
    # outband.SetNoDataValue(np.nan)
    outband.WriteArray(array)   #将数据写入获取的这个波段中（写入的数据只能是二维的）
    outRaster.FlushCache()
    del outRaster

if __name__ == "__main__":
    for key in sorted(Disaster_Province_1Level_List):
        for each_province in Disaster_Province_1Level_List[key]:
            Province_Name_shorthand = each_province
            Country_Name_shorthand = key

            print(Province_Name_shorthand, Country_Name_shorthand)

            Disaster_Occur_Time = Disaster_Occur_Time_List[key][0]

            # 基于Country_Name_shorthand解析出国家缩写，数据收集的开始与结束时间
            Country_Name_shorthand_List = Country_Name_shorthand.split("_")
            Country_Code = Country_Name_shorthand_List[0]
            Start_Time_Str = Country_Name_shorthand_List[1]
            End_Time_Str = Country_Name_shorthand_List[2]

            # 构建需要读取的影像文件夹，以及基于掩码文件生成的夜光影像文件保存路径，并从文件夹中获取需要处理的所有文件路径，以及文件名
            NTL_File_dic = "G:\\postgraduate\\postgraduate_bishe\\VNP46A2_tif\\DNB_BRDF-Corrected_NTL_joint_clip_" + Province_Name_shorthand + "_Masked\\"
            NTL_File_Path, NTL_File_Name = generateHDF5FilePath(NTL_File_dic)

            # 生成灾前灾后均值合成影像，返回合成后的数组以及空间参考信息
            pre_disaster_img_array, post_disaster_img_array, geoTransform_reference, proj_reference, NaN_Value_reference = generateDisasterPreAndPostMeanImg(NTL_File_Path, NTL_File_Name, Disaster_Occur_Time)

            # 构建合成影像的保存文件夹路径
            output_dir_path = "G:\\postgraduate\\postgraduate_bishe\\VNP46A2_tif\\pre_and_post_disaster_mean_NTL_Img\\"
            # 判断输出路径的文件夹是否存在，不存在则创建一个
            if not os.path.exists(output_dir_path):
                os.makedirs(output_dir_path)
            # 构建合成影像的文件路径
            pre_disasterImg_output_path = output_dir_path + Province_Name_shorthand + "_pre_10days_disaster_Img.tif"
            post_disasterImg_output_path = output_dir_path + Province_Name_shorthand + "_post_3month_disaster_Img.tif"

            # 生成tif影像
            array2raster(pre_disasterImg_output_path, pre_disaster_img_array, geoTransform_reference, proj_reference, NaN_Value_reference)
            print(pre_disasterImg_output_path, "has finished...")
            array2raster(post_disasterImg_output_path, post_disaster_img_array, geoTransform_reference, proj_reference, NaN_Value_reference)
            print(post_disasterImg_output_path, "has finished...")

            # 曼-惠特尼U检验
            pre_disaster_img_array_1dim = pre_disaster_img_array.flatten()
            post_disaster_img_array_1dim = post_disaster_img_array.flatten()
            pre_disaster_img_array_1dim_withoutNaN = pre_disaster_img_array_1dim[np.logical_not(np.isnan(pre_disaster_img_array_1dim))]
            post_disaster_img_array_1dim_withoutNaN = post_disaster_img_array_1dim[np.logical_not(np.isnan(post_disaster_img_array_1dim))]
            statistic_result = stats.mannwhitneyu(pre_disaster_img_array_1dim_withoutNaN, post_disaster_img_array_1dim_withoutNaN, alternative = None)
            print(statistic_result)
            print("pre-disaster image max NTL value:", np.nanmax(pre_disaster_img_array))
            print("post-disaster image max NTL value:",np.nanmax(post_disaster_img_array))

            # weight_high = [134, 146, 104, 119, 124, 161, 107, 83, 113, 129, 97, 123]
            # weight_low = [70, 118, 101, 85, 112, 132, 94]
            # print(stats.mannwhitneyu(weight_high, weight_low, alternative='two-sided'))