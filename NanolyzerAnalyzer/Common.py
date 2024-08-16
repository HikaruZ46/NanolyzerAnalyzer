import numpy as np


class H:
    duration_us = "duration_us"
    id = 'id'
    type = 'type'
    start_time_s = 'start_time_s'
    end_time_s = 'end_time_s'
    event_sep_time_s = 'event_sep_time_s'
    effective_baseline_pA = 'effective_baseline_pA'
    area_pC = 'area_pC'
    average_blockage_pA = 'average_blockage_pA'
    max_blockage_pA = 'max_blockage_pA'
    max_blockage_duration_us = 'max_blockage_duration_us'
    log_max_blockage_duration_us = 'log_max_blockage_duration_us'
    n_levels = 'n_levels'
    residual_pA = 'residual_pA'
    max_deviation_pA = 'max_deviation_pA'
    min_blockage_pA = 'min_blockage_pA'
    min_blockage_duration_us = 'min_blockage_duration_us'
    log_min_blockage_duration_us = 'log_min_blockage_duration_us'
    rise_time_in_us = 'rise_time_in_us'
    rise_time_out_us = 'rise_time_out_us'
    intra_crossings = 'intra_crossings'
    level_current_pA = 'level_current_pA'
    level_duration_us = 'level_duration_us'
    blockages_pA = 'blockages_pA'
    stdev_pA = 'stdev_pA'
    level_num = 'level_num'
    levels_left = 'levels_left'
    intra_crossing_times_us = 'intra_crossing_times_us'
    average_blockage_ratio = 'average_blockage_ratio'
    max_blockage_ratio = 'max_blockage_ratio'
    log_duration_us = 'log_duration_us'
    Voltage = 'Voltage'
    sample_type = 'sample_type'
    average_fractional_blockade = 'average_fractional_blockade'
    max_fractional_blockade = 'max_fractional_blockade'
    max_delta_g = 'max_delta_g(nS)'
    average_delta_g = 'average_delta_g(nS)'
    fractional_blockade = 'frac'
    delta_i = '# deli'
    dwell_time = 'dwell'
    dt = 'dt'
    logged_dwell_time = 'logged_dwell_time'
    Voltage = 'Voltage'
    type = 'type'
    startpoints = 'startpoints'
    endpoints = 'endpoints'
    event_septimes = 'event_septimes'
    time_us = 'time_us'
    current_pA = 'current_pA'
    fitted_current_pA = 'fitted_current_pA'
    curve_fitted_current_pA = 'curve_fitted_current_pA'
    file_name = 'file_name'

class datatype :
    raw = 'raw'
    zeroed = 'zeroed'
    g = 'g'
    delta_g = 'delta_g'
    normalized = 'normalized'


def final_value_converter(arr:np.ndarray, value = None) -> np.ndarray :
    if np.unique(arr).shape[0] == 1 :
        return arr
    if value == None :
        value = np.max(arr) + 1
    n = len(arr)-np.where(arr[1:] != arr[:-1])[0][-1]-1
    arr1 = arr.copy()
    arr1[-n:] = value
    return arr1

def zip_data(data:np.ndarray) -> np.ndarray :
    change_ind = np.concatenate(([data[0]],np.where(data[:-1] != data[1:])[0]+1))
    ind_diff = np.diff(change_ind)
    zip_data = data[change_ind]
    zip_counts = np.concatenate((ind_diff, [len(data)-change_ind[-1]]))
    return np.array([zip_data, zip_counts])

# smoothing(arr, min_frame)でmin_frame以下のstepを除去し，前のステップと同じものにする。
# 将来的には前のステップと同じではなく，前後に半分ずつに分けたい。
# convert_goalでgoalの値のみを変換できる。defaultはNoneで，Noneの場合は変更しない。convert_goal=5とかとすれば最後が全部5になる。

def smoothing(arr : np.array, min_frame : int) :
    count = 1
    # counts_list = [count]
    templist = []
    temp_value = arr[0]
    for i in range(1, len(arr)) :
        if arr[i] == arr[i-1] :
            count += 1
        else :
            if count > min_frame : 
                templist.extend(arr[i-count:i].tolist())
                temp_value = arr[i-1]
            else :
                templist.extend([temp_value for j in range(count)])
            count = 1
        # counts_list.append(count)
    templist.extend(arr[-count:].tolist()) 
    return np.array(templist)

