import random
from datetime import datetime

def d_to_jd(time):
    fmt = '%Y.%m.%d'
    dt = datetime.strptime(time, fmt)
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday

def jd_to_time(time):
    dt = datetime.strptime(time, '%Y%j').date()
    fmt = '%Y.%m.%d'
    return dt.strftime(fmt)

def getRandomIndex_crossValidationK(allData_Index, total_size, select_size, crossValidation_count):
    randomIndex_list = []   # 存放生成的crossValidation_count组验证数据索引
    alreadyUseIndex = []    # 保存已经选取的索引，防止数据重复

    for i in range(crossValidation_count):
        randomIndex_list_array = []
        while(len(randomIndex_list_array) != select_size):
            randNum = random.randint(0, total_size-1)
            if (randNum not in alreadyUseIndex):
                randomIndex_list_array.append(allData_Index[randNum])
                alreadyUseIndex.append(randNum)
        randomIndex_list.append(randomIndex_list_array)
    return randomIndex_list

def processPixelTimeSeries(line, time_list, normalized_ntl_list, vza_list, allData_Index, start_time, end_time):
    start_time_day = str(d_to_jd(start_time[:4] + "." + start_time[4:6] + "." +start_time[6:]))[4:]
    end_time_day = str(d_to_jd(end_time[:4] + "." + end_time[4:6] + "." +end_time[6:]))[4:]

    i_count = 0
    list_index = 0  # 用于记录添加到列表时的索引

    line_list = line.split(":")
    key = line_list[0]
    pointLngLat = line_list[1]
    timeSeries_list = line_list[2].split(";")
    # 先判断第一天
    firstTime = timeSeries_list[0].split(',')[0]
    current_time = d_to_jd(firstTime[:4] + "." + firstTime[4:6] + "." +firstTime[6:])
    # 如果第一天不是20221/1时，需要把前面的数据也补上(不同数据需要区别对待)
    if (str(current_time)[-3:] != start_time_day):
        before_time = str(current_time)[:-3] + start_time_day
        before_time = int(before_time)
        diff_count = current_time - before_time
        for j in range(diff_count):
            YYYYMMDD_list = jd_to_time(str(before_time + j)).split('.')
            time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
            normalized_ntl_list.append(float(65535))
            list_index += 1

    for i in range(len(timeSeries_list)-1):
        i_count = i
        info = timeSeries_list[i].split(',')
        time = info[0]
        vaz = info[1]
        normalized_ntl = info[2]

        info_next = timeSeries_list[i+1].split(',')
        time_next = info_next[0]
        vaz_next = info_next[1]
        normalized_ntl_next = info_next[2]

        last_time = d_to_jd(time_next[:4] + "." + time_next[4:6] + "." + time_next[6:])
        pre_time = d_to_jd(time[:4] + "." + time[4:6] + "." + time[6:])
        diff_count = int(last_time) - int(pre_time)

        if (diff_count > 1 and diff_count < 365):
            time_list.append(int(time))
            normalized_ntl_list.append(float(normalized_ntl))
            allData_Index.append(int(list_index))
            list_index += 1

            for j in range(1, diff_count):
                YYYYMMDD_list = jd_to_time(str(int(pre_time) + j)).split('.')
                time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
                normalized_ntl_list.append(float(65535))
                list_index += 1
        # 存在跨年的问题
        elif (diff_count > 365):
            # 先把这一天添加进去
            time_list.append(int(time))
            normalized_ntl_list.append(float(normalized_ntl))
            allData_Index.append(int(list_index))
            list_index += 1

            year_temp = int(str(pre_time)[0:4])
            day_temp = int(str(pre_time)[4:])
            if (year_temp % 4 == 0):
                if (day_temp < 366):
                    for i in range(366 - day_temp):
                        YYYYMMDD_list = jd_to_time(str(int(pre_time) + i + 1)).split('.')
                        time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
                        normalized_ntl_list.append(float(65535))
                        list_index += 1
            else:
                if (day_temp < 365):
                    for i in range(365 - day_temp):
                        YYYYMMDD_list = jd_to_time(str(int(pre_time) + i + 1)).split('.')
                        time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
                        normalized_ntl_list.append(float(65535))
                        list_index += 1

            # 上一年补全之后，下一年不是从1开始
            if (str(last_time)[-3:] != "001"):
                before_time = str(last_time)[:-3] + "001"
                before_time = int(before_time)
                diff_count = last_time - before_time
                for j in range(diff_count):
                    YYYYMMDD_list = jd_to_time(str(before_time + j)).split('.')
                    time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
                    normalized_ntl_list.append(float(65535))
                    list_index += 1
        else:
            time_list.append(int(time))
            normalized_ntl_list.append(float(normalized_ntl))
            allData_Index.append(int(list_index))
            list_index += 1

    info_last = timeSeries_list[i_count + 1].split(',')
    time_last = info_last[0]
    vaz_last = info_last[1]
    normalized_ntl_last = info_last[2]
    time_list.append(int(time_last))
    normalized_ntl_list.append(float(normalized_ntl_last))
    allData_Index.append(int(list_index))
    list_index += 1
    end_time = d_to_jd(time_last[:4] + "." + time_last[4:6] + "." + time_last[6:])
    year = int(str(end_time)[0:4])
    day = int(str(end_time)[4:])

    # 如果最后一天不是20235/1时，需要把后面的数据也补上(不同数据需要区别对待)
    if (str(end_time)[-3:] != end_time_day):
        after_time = str(end_time)[:-3] + end_time_day
        after_time = int(after_time)
        before_time = int(end_time)
        diff_count = after_time - before_time
        for j in range(diff_count):
            YYYYMMDD_list = jd_to_time(str(before_time + j + 1)).split('.')
            time_list.append(int(str(YYYYMMDD_list[0]) + str(YYYYMMDD_list[1]) + str(YYYYMMDD_list[2])))
            normalized_ntl_list.append(float(65535))
            list_index += 1

    return key
def loadData(file_path, start_time, end_time):
    contents = open(file_path)
    lines = contents.readlines()
    txtFormat = ""

    datasets = []
    key_list = []
    for row in range(len(lines)):
        if (row == 0):
            txtFormat = lines[row]
        else:
            time_list = []
            normalized_ntl_list = []
            vza_list = []
            allData_Index = []
            key = processPixelTimeSeries(lines[row].strip(), time_list, normalized_ntl_list, vza_list, allData_Index, start_time, end_time)
            key_list.append(key)

            # 基于组织的数据进行随机分组
            valid_data_rate = 0.05
            valid_data_size = int(len(allData_Index) * valid_data_rate)
            if (valid_data_size == 0):
                valid_data_size = 1
            crossValidation_count = int(len(allData_Index) / valid_data_size)

            # 生成随机挑选的测试数据索引，（索引是针对allData_Index的索引）
            randomIndex_list = getRandomIndex_crossValidationK(allData_Index, len(allData_Index), valid_data_size, crossValidation_count)
            all_crossValidation_validationData_Index = []
            all_crossValidation_trianingData_Index = []
            for cross_index in range(crossValidation_count):
                validationData_Index = randomIndex_list[cross_index]    # 所有数据（包含缺值）中验证数据对应的索引
                trianingData_Index = []                                 # 所有数据（包含缺值）中训练数据对应的索引

                for index in range(len(allData_Index)):
                    if (allData_Index[index] not in validationData_Index):
                        trianingData_Index.append(allData_Index[index])
                all_crossValidation_validationData_Index.append(validationData_Index)
                all_crossValidation_trianingData_Index.append(trianingData_Index)

            datasets.append([time_list, normalized_ntl_list, allData_Index, all_crossValidation_trianingData_Index, all_crossValidation_validationData_Index, key_list])
        print(row, "line read...")

    return datasets

if __name__ == "__main__":
    start_time = "20180121"
    end_time = "20190120"
    # start_time = "20220101"
    # end_time = "20230501"
    # file_path = "D:\\VZA_Article\\data\\event_longTime\\id18_20180121_20190120\\new_method\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_Arecibo"
    file_path = "D:\\VZA_Article\\data\\event_longTime\\id18_20180121_20190120\\represent_pixel_datafilling\\TS_output_withoutMoonIlluminationAndSnow_fit_result_gradientDescent_1%_1invalid_Arecibo"
    datasets = loadData(file_path, start_time, end_time)

    aaa = 10