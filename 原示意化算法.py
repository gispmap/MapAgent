import math
import matplotlib.pyplot as plt
import numpy as np


def calculate_azimuth(lat1, lon1, lat2, lon2):
    delta_x = lon2 - lon1
    delta_y = lat2 - lat1
    theta = math.degrees(math.atan2(delta_y, delta_x))
    return theta


def calculate_distance(lat1, lon1, lat2, lon2):
    # 使用Haversine公式计算地球表面两点间的距离
    R = 6371.0 # 地球半径，单位为公里

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c * 1000  # 转换为米
    distance = round(distance, 2)
    return distance


def calculate_new_coordinates(lat1, lon1, distance, azimuth):
    # 将方位角从度转换为弧度
    azimuth = math.radians(azimuth)

    # 计算距离转换后的经纬度差值
    delta_x = distance * math.cos(azimuth)
    delta_y = distance * math.sin(azimuth)

    # 计算新的经纬度
    new_lon = lon1 + delta_x / 111320  # 1度经度大约等于111.32公里
    new_lat = lat1 + delta_y / 110540  # 1度纬度大约等于110.54公里

    new_lon = round(new_lon, 6)
    new_lat = round(new_lat, 6)

    return new_lat, new_lon


def get_adjusted_azimuth(azimuth):
    if -22.5 < azimuth <= 22.5:
        return 0
    elif 22.5 <= azimuth < 67.5:
        return 45
    elif 67.5 <= azimuth < 112.5:
        return 90
    elif 112.5 <= azimuth < 157.5:
        return 135
    elif 157.5 <= azimuth <= 180:
        return 180
    elif -180<= azimuth < -157.5:
        return -180
    elif -157.5 <= azimuth < -112.5:
        return -135
    elif -112.5 <= azimuth < -67.5:
        return -90
    elif -67.5 <= azimuth < -22.5:
        return -45


def get_new_adjusted_azimuth(azimuthlist):
    adjusted_azimuths = []
    for item in azimuthlist:
        if -22.5 < item <= 22.5:
            adjusted_azimuths.append(0)
        elif 22.5 <= item < 67.5:
            adjusted_azimuths.append(45)
        elif 67.5 <= item < 112.5:
            adjusted_azimuths.append(90)
        elif 112.5 <= item < 157.5:
            adjusted_azimuths.append(135)
        elif 157.5 <= item <= 180:
            adjusted_azimuths.append(180)
        elif -180 <= item < -157.5:
            adjusted_azimuths.append(-180)
        elif -157.5 <= item < -112.5:
            adjusted_azimuths.append(-135)
        elif -112.5 <= item < -67.5:
            adjusted_azimuths.append(-90)
        elif -67.5 <= item < -22.5:
            adjusted_azimuths.append(-45)

    # 查找重叠线路
    for i in range(len(adjusted_azimuths) - 1):
        angle_a = abs(adjusted_azimuths[i])
        angle_b = abs(adjusted_azimuths[i + 1])
        if (angle_a + angle_b == 180) and ((180 > adjusted_azimuths[i] > 0 > adjusted_azimuths[i + 1] > -180) or (
                -180 < adjusted_azimuths[i] < 0 < adjusted_azimuths[i + 1] < 180)):
            if azimuthlist[i + 1] > adjusted_azimuths[i + 1]:
                adjusted_azimuths[i + 1] = adjusted_azimuths[i + 1] + 45
            elif azimuthlist[i + 1] <= adjusted_azimuths[i + 1]:
                adjusted_azimuths[i + 1] = adjusted_azimuths[i + 1] - 45
        elif (angle_a + angle_b == 180) and ((adjusted_azimuths[i] == 0 and (
                adjusted_azimuths[i + 1] == 180 or adjusted_azimuths[i + 1] == -180)) or (
                                                     (adjusted_azimuths[i] == -180 or adjusted_azimuths[i] == 180) and
                                                     adjusted_azimuths[i + 1] == 0)):
            # if azimuthList[i + 1] > adjusted_azimuths[i + 1]:
            #         adjusted_azimuths[i + 1] = adjusted_azimuths[i + 1] + 45
            # elif azimuthList[i + 1] <= adjusted_azimuths[i + 1]:
            #         adjusted_azimuths[i + 1] = adjusted_azimuths[i + 1] - 45
            if adjusted_azimuths[i + 1] == 180:
                adjusted_azimuths[i + 1] = 90
            elif adjusted_azimuths[i + 1] == -180:
                adjusted_azimuths[i + 1] = -90
            elif adjusted_azimuths[i + 1] == 0:
                if azimuthlist[i + 1] > 0:
                    adjusted_azimuths[i + 1] = 90
                elif azimuthlist[i + 1] <= 0:
                    (
                        adjusted_azimuths)[i + 1] = -90
    return adjusted_azimuths



def get_adjusted_distance(distance):
    return 2000


def init_dist_azi(Plist):
    # 初始距离列表
    dist = []
    # 初始角度列表
    azimuth = []
    for i in range(len(Plist) - 1):
        lat1, lon1 = Plist[i]
        lat2, lon2 = Plist[i + 1]
        # 计算初始方位角和距离
        initial_azimuth = calculate_azimuth(lat1, lon1, lat2, lon2)
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        azimuth.append(initial_azimuth)
        dist.append(distance)
    return dist, azimuth


def adjusted(Plist, dist, azimuth):
    #新坐标
    adjusted_coords = [Plist[0]]

    #新角度
    adjusted_azimuths = []

    #新距离
    adjusted_dists = []

    for i in range(len(Plist) - 1):

        new_dist = get_adjusted_distance(dist[i])

        adjusted_dists.append(new_dist)
        # 调整方位角
        adjusted_azimuth = get_adjusted_azimuth(azimuth[i])
        adjusted_azimuths.append(adjusted_azimuth)

        # 根据调整后的方位角和距离计算新的坐标
        new_lat1, new_lon1 = adjusted_coords[i]
        new_lat2, new_lon2 = calculate_new_coordinates(new_lat1, new_lon1, adjusted_dists[i], adjusted_azimuth)
        adjusted_coords.append([new_lat2, new_lon2])
        new_lat1, new_lon1 = new_lat2, new_lon2
    return  adjusted_coords


def draw_map(ax, adjusted_coords):
    x = [lon for lat, lon in adjusted_coords]
    y = [lat for lat, lon in adjusted_coords]
    ax.scatter(x, y, color='blue')

    # 标注点号
    for i, (lat, lon) in enumerate(adjusted_coords):
        ax.text(lon, lat, f'{i + 1}', fontsize=12, ha='right')

    # 绘制调整后的线段和标注
    for i in range(len(adjusted_coords) - 1):
        lon1, lat1 = adjusted_coords[i][1], adjusted_coords[i][0]
        lon2, lat2 = adjusted_coords[i + 1][1], adjusted_coords[i + 1][0]

        ax.plot([lon1, lon2], [lat1, lat2], color='red', linestyle='-')
    ax.set_xticks([])  # 隐藏x轴刻度
    ax.set_yticks([])  # 隐藏y轴刻度


# 坐标列表
CoorList = [
    [39.908653, 116.397487],
    [39.916345, 116.397155],
    [39.999998, 116.275241],
    [39.883708, 116.412774],
    [39.941264, 116.333161],
    [39.908247, 116.397954],
    [39.935451, 116.403784],
    [39.92908, 116.38975],
    [39.92978, 116.38532],
    [39.90566, 116.398435],
    [40.357322, 116.021746],
    [39.992809, 116.388781],
    [39.99152, 116.38749]]

dist, azimuth = init_dist_azi(CoorList)
adjusted_coords = adjusted(CoorList, dist, azimuth)

fig, ax = plt.subplots(1, 2)

draw_map(ax[0], CoorList)
draw_map(ax[1], adjusted_coords)
plt.show()
