from datetime import datetime
import glob
import os

OECD_Country_List = {
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
    rasters = glob.glob(os.path.join(folderPath, "*.h5"))
    Name_List = []
    for i in range(len(rasters)):
        Name = rasters[i].split("\\")[-1][:-21]
        Name_List.append(Name)
    return rasters, Name_List


if __name__ == "__main__":
    # 只需要把国家名称简写 Country_Name_shorthand
    # 起止时间  start_time, end_time
    # 下载好的文件夹路径 H5Files_Path
    # 设置好，即可得到缺失文件的Tile及Time
    Country_Name_shorthand = "TURSYR_20230501_20240208"

    # 以下内容可以都不用改
    Country_Name_shorthand_List = Country_Name_shorthand.split("_")
    Country_Code = Country_Name_shorthand_List[0]
    Start_Time_Str = Country_Name_shorthand_List[1]
    End_Time_Str = Country_Name_shorthand_List[2]
    H5Files_Path = "G:\\postgraduate\\postgraduate_bishe\\VNP46A2_res_res\\"
    # H5Files_Path = "G:\\disaster_research_OECD_country_data\\JPN\\20200329_20200729\\"
    start_time = Start_Time_Str[:4] + "." + Start_Time_Str[4:6] + "." + Start_Time_Str[6:]
    end_time = End_Time_Str[:4] + "." + End_Time_Str[4:6] + "." + End_Time_Str[6:]
    # start_time = "2020.03.29"
    # end_time = "2020.07.29"

    H5Files_Path_List, H5Files_Name_List = generateHDF5FilePath(H5Files_Path)
    # print(H5Files_Name_List)
    Country_Tiles_List = OECD_Country_List[Country_Name_shorthand]
    print(Country_Tiles_List)
    TimePeriod_list = generateTimePeriod(start_time, end_time)
    # print(TimePeriod_list)
    count = 0
    for i in range(len(Country_Tiles_List)):
        for j in range(len(TimePeriod_list)):
            temp_name = "VNP46A2.A" + str(TimePeriod_list[j]) + "." + str(Country_Tiles_List[i])
            # print(temp_name)
            # print(temp_name in H5Files_Name_List)
            if (temp_name not in H5Files_Name_List):
                count += 1
                print("Tile:",Country_Tiles_List[i], "Time:",jd_to_time(str(TimePeriod_list[j])), "DOY:", TimePeriod_list[j])
    print("miss ", count, " data")
    print(len(OECD_Country_List))

'''
A1
h20v04: 2022.07.27(2022208)-2022.08.10(2022222)
h20v05: 2022.07.27(2022208)-2022.08.10(2022222)
h21v04: 2022.07.27(2022208)-2022.08.10(2022222)
h21v05: 2022.07.26(2022207)-2022.08.10(2022222)
h22v04: 2022.07.26(2022207)-2022.08.10(2022222)
h22v05: 2022.07.26(2022207)-2022.08.10(2022222)

A2
h20v04: 2022.07.27(2022208)-2022.08.10(2022222) 2022.06.28(2022179)
h20v05: 2022.07.27(2022208)-2022.08.10(2022222) 2022.06.28(2022179)
h21v04: 2022.07.27(2022208)-2022.08.10(2022222) 2022.06.28(2022179)
h21v05: 2022.07.26(2022207)-2022.08.10(2022222) 2022.06.28(2022179)
h22v04: 2022.07.26(2022207)-2022.08.10(2022222) 2022.06.28(2022179)
h22v05: 2022.07.26(2022207)-2022.08.10(2022222) 2022.06.28(2022179)
'''


'''
A1
h21v05 Time: 2023.11.01 DOY: 2023305
h22v04 Time: 2023.11.01 DOY: 2023305
h22v05 Time: 2023.11.01 DOY: 2023305
'''

'''
A2
h20v04 Time: 2023.07.26 (2023207)
             2023.07.27 DOY: 2023208
             2023.11.02 DOY: 2023306
             2024.01.31 DOY: 2024031
             
h20v05 Time: 2023.07.26 DOY: 2023207
             2023.07.27 DOY: 2023208
             2023.11.02 DOY: 2023306
             2024.01.31 DOY: 2024031
             
h21v04 Time: 2023.07.26 DOY: 2023207
             2023.07.27 DOY: 2023208
             2023.11.02 DOY: 2023306
             2024.01.31 DOY: 2024031
             
h21v05 Time: 2023.07.26 DOY: 2023207
             2023.07.27 DOY: 2023208
             
             2023.11.01 DOY: 2023305
             
             2023.11.02 DOY: 2023306
             2024.01.31 DOY: 2024031
             
h22v04 Time: 2023.07.26 DOY: 2023207
             2023.07.27 DOY: 2023208
             2023.11.01 DOY: 2023305
             2023.11.02 DOY: 2023306
             2024.01.31 DOY: 2024031
             
h22v05 Time: 2023.07.26 DOY: 2023207
             2023.07.27 DOY: 2023208
             2023.11.01 DOY: 2023305
             2023.11.02 DOY: 2023306
             2024.01.31 DOY: 2024031
'''



# def generateTimePeriod(start_tm, end_tm):
#     TimePeriod_list = []
#
#     jd_start_time = d_to_jd(start_tm)
#     jd_end_time = d_to_jd(end_tm)
#
#     print(jd_start_time,jd_end_time)
#
#     start_year = int(str(jd_start_time)[:4])
#     end_year = int(str(jd_end_time)[:4])
#
#     # 同一年的情况
#     if (start_year == end_year):
#         diff_time = jd_end_time - jd_start_time + 1
#         for i in range(diff_time):
#             TimePeriod_list.append(jd_start_time + i)
#     else:
#         # 只相差一年
#         if (end_year - start_year == 1):
#             # 闰年的判断
#             if (start_year % 4 == 0):
#                 temp_jd_end_time = int(str(start_year) + "366")
#             else:
#                 temp_jd_end_time = int(str(start_year) + "365")
#
#             temp_diff_time = temp_jd_end_time - jd_start_time + 1
#             for i in range(temp_diff_time):
#                 TimePeriod_list.append(jd_start_time + i)
#
#             temp_jd_start_time = int(str(end_year) + "001")
#             temp_diff_time = jd_end_time - temp_jd_start_time + 1
#             for i in range(temp_diff_time):
#                 TimePeriod_list.append(temp_jd_start_time + i)
#
#         # 不同年情况
#         else:
#             diff_year = end_year - start_year + 1
#             for i in range(diff_year):
#                 temp_start_year = start_year + i
#
#                 if (i == 0):
#                     if (temp_start_year % 4 == 0):
#                         temp_jd_end_time = int(str(temp_start_year) + "366")
#                     else:
#                         temp_jd_end_time = int(str(temp_start_year) + "365")
#                     temp_diff_time = temp_jd_end_time - jd_start_time + 1
#                     for j in range(temp_diff_time):
#                         TimePeriod_list.append(jd_start_time + j)
#                 elif (i == diff_year - 1):
#                     temp_jd_start_time = int(str(temp_start_year) + "001")
#                     temp_diff_time = jd_end_time - temp_jd_start_time + 1
#                     for j in range(temp_diff_time):
#                         TimePeriod_list.append(temp_jd_start_time + j)
#                 else:
#                     temp_jd_start_time = int(str(temp_start_year) + "001")
#                     if (temp_start_year % 4 == 0):
#                         temp_diff_time = 366
#                     else:
#                         temp_diff_time = 365
#                     for j in range(temp_diff_time):
#                         TimePeriod_list.append(temp_jd_start_time + j)
#
#
#     print("******")
#     for each in TimePeriod_list:
#         print(each)




