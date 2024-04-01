import gdal
import numpy as np

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

if __name__ == "__main__":

    # 构建需要读取的夜光影像与掩码影像文件夹，以及夜光影像与掩码影像对应保存的文件夹路径，同时构建用于裁剪参考的gadm文件路径
    File_Path = "G:\\postgraduate\\postgraduate_bishe\\VNP46A2_tif\\pre_and_post_disaster_mean_NTL_Img\\Antakya"
    File_Path_pre = File_Path + "_pre_10days_disaster_Img.tif"
    File_Path_post1 = File_Path + "_post_10days_disaster_Img.tif"
    File_Path_post2 = File_Path + "_post_1month_disaster_Img.tif"
    File_Path_post3 = File_Path + "_post_3month_disaster_Img.tif"

    raster_NTL_pre, geoTransform_NTL_pre, proj_NTL_pre, NaN_Value_NTL_pre = read_tiff(File_Path_pre)
    raster_NTL_post1, geoTransform_NTL_post1, proj_NTL_post1, NaN_Value_NTL_post1 = read_tiff(File_Path_post1)
    raster_NTL_post2, geoTransform_NTL_post2, proj_NTL_post2, NaN_Value_NTL_post2 = read_tiff(File_Path_post2)
    raster_NTL_post3, geoTransform_NTL_post3, proj_NTL_post3, NaN_Value_NTL_post3 = read_tiff(File_Path_post3)

    raster_NTL_pre_1dim = raster_NTL_pre.flatten()
    raster_NTL_pre_1dim_without_nan = raster_NTL_pre_1dim[~np.isnan(raster_NTL_pre_1dim)] / 10.0

    raster_NTL_post1_1dim = raster_NTL_post1.flatten()
    raster_NTL_post1_1dim_without_nan = raster_NTL_post1_1dim[~np.isnan(raster_NTL_post1_1dim)] / 10.0

    raster_NTL_post2_1dim = raster_NTL_post2.flatten()
    raster_NTL_post2_1dim_without_nan = raster_NTL_post2_1dim[~np.isnan(raster_NTL_post2_1dim)] / 10.0

    raster_NTL_post3_1dim = raster_NTL_post3.flatten()
    raster_NTL_post3_1dim_without_nan = raster_NTL_post3_1dim[~np.isnan(raster_NTL_post3_1dim)] / 10.0

    print("pre 1 month: ", np.sum(raster_NTL_pre_1dim_without_nan))
    print("post 10 day: ", np.sum(raster_NTL_post1_1dim_without_nan))
    print("post 1 month: ", np.sum(raster_NTL_post2_1dim_without_nan))
    print("post 3 month: ", np.sum(raster_NTL_post3_1dim_without_nan))
    a = 10
