# -*- coding: utf-8 -*-
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
    NaN_Value = dt.GetNoDataValue()  # 得到影像中nodata的数值
    data = dt.ReadAsArray(0,0,row,col) # Getting data from 0 rows and 0 columns
    del datasets
    return data,geoTransform,proj, NaN_Value

if __name__ == "__main__":
    data, geoTransform,proj, NaN_Value = read_tiff('G:\\postgraduate\\postgraduate_bishe\\VNP46A2_tif\\DNB_BRDF-Corrected_NTL_joint_clip_TUR_noTranslation\\2022003_joint_image_TUR_Clp.tif')
    a = 10