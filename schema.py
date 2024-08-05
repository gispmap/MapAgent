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
    R = 6371.0  # 地球半径，单位为公里

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
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


def get_adjusted_azimuth(azimuthlist):
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

    print(adjusted_azimuths)
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
    print(adjusted_azimuths)
    return adjusted_azimuths


#对数变化距离
def log_transformed_dist(distanceList):
    #指定缩放范围
    min_target = 1000
    max_target = 5000
    # 对数变换然后缩放
    log_transformed = np.log1p(distanceList)  # log1p用于避免log(0)问题
    log_min = min(log_transformed)
    log_max = max(log_transformed)
    log_scaled_distances = [(x - log_min) / (log_max - log_min) * (max_target - min_target) + min_target for x in
                            log_transformed]

    # 四舍五入取整
    log_scaled_distances = [int(round(x)) for x in log_scaled_distances]
    return log_scaled_distances


def sqrt_transformed_dist(distanceList):
    # 指定缩放范围
    min_target = 3500
    max_target = 5000
    #平方根变换
    sqrt_transformed = np.sqrt(distanceList)
    sqrt_min = min(sqrt_transformed)
    sqrt_max = max(sqrt_transformed)
    sqrt_scaled_distances = [(x - sqrt_min) / (sqrt_max - sqrt_min) * (max_target - min_target) + min_target for x in
                             sqrt_transformed]

    # 四舍五入取整
    log_scaled_distances = [int(round(x)) for x in sqrt_scaled_distances]
    return log_scaled_distances


def init_dist_azi(Plist):
    #初始距离列表
    dist = []
    #初始角度列表
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


def adjusted(Plist, adjusted_dists, adjusted_azimuths):
    #新坐标
    adjusted_coords = [Plist[0]]

    # 根据调整后的方位角和距离计算新的坐标
    for i in range(len(Plist) - 1):
        new_lat1, new_lon1 = adjusted_coords[i]
        # 根据调整后的方位角和距离计算新的坐标
        new_lat2, new_lon2 = calculate_new_coordinates(new_lat1, new_lon1, adjusted_dists[i], adjusted_azimuths[i])
        adjusted_coords.append([new_lat2, new_lon2])
        new_lat1, new_lon1 = new_lat2, new_lon2
    return adjusted_coords


# def draw_map(adjusted_coords):
#     # 创建绘图
#     plt.figure(figsize=(10, 10))
#     x = [lon for lat, lon in adjusted_coords]
#     y = [lat for lat, lon in adjusted_coords]
#     plt.scatter(x, y, color='blue')
#
#     # 标注点号
#     for i, (lat, lon) in enumerate(adjusted_coords):
#         plt.text(lon, lat, f'{i + 1}', fontsize=12, ha='right')
#
#     # 绘制调整后的线段和标注
#     for i in range(len(adjusted_coords) - 1):
#         lon1, lat1 = adjusted_coords[i][1], adjusted_coords[i][0]
#         lon2, lat2 = adjusted_coords[i + 1][1], adjusted_coords[i + 1][0]
#
#         plt.plot([lon1, lon2], [lat1, lat2], color='red', linestyle='-')
#
#     plt.xlabel('Longitude')
#     plt.ylabel('Latitude')
#     plt.title('Adjusted Coordinate Points with Azimuth and Distance')
#     plt.grid(True)
#     plt.show()

def draw_map(adjusted_coords):
    colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'orange', ]
    # 创建绘图
    plt.figure(figsize=(10, 10))
    x_coor = []
    y_coor = []
    for i in range(len(adjusted_coords)):
        for lat, lon in adjusted_coords[i]:
            x_coor.append(lon)
            y_coor.append(lat)
    plt.scatter(x_coor, y_coor, color='blue')

    # 标注点号
    target = 0
    for i in range(len(adjusted_coords)):
        for index, (lat, lon) in enumerate(adjusted_coords[i]):
            plt.text(lon, lat, f'{target + 1}', fontsize=12, ha='right')
            target += 1

    # 绘制调整后的线段和标注
    index = 0
    for j in range(len(adjusted_coords)):
        for i in range(len(adjusted_coords[j])):
            if index < (len(x_coor) - 1):
                lon1, lat1 = x_coor[index], y_coor[index]
                lon2, lat2 = x_coor[index + 1], y_coor[index + 1]
                plt.plot([lon1, lon2], [lat1, lat2], color=colors[j], linestyle='-')
                print(index)
                index += 1

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Adjusted Coordinate Points with Azimuth and Distance')
    plt.grid(True)
    plt.show()


# 坐标列表
CoorList = [
    [[39.908719, 116.397479],
     [39.916345, 116.397155],
     [39.912469, 116.403909]],
    [[39.933176, 116.407358],
     [39.924091, 116.396907]],
    [[39.999976, 116.275461],
     [40.002189, 116.326503],
     [40.008152, 116.304508]]
]

CoorList2 = [
    [[39.908722, 116.397499],
     [39.916345, 116.397155],
     [39.929986, 116.394547],
     [39.924399, 116.389155],
     [39.912586, 116.409667]],
    [[39.999975, 116.273057],
     [40.007978, 116.299293]],
    [[39.998003, 116.317458],
     [40.002217, 116.327391],
     [39.938883, 116.333304]],
    [[40.431908, 116.570374],
     [40.253530, 116.144951]],
    [[39.992079, 116.390501],
     [39.992933, 116.396546]]
]

draw_map(CoorList2)

init_dists, init_angles = init_dist_azi(CoorList)
print(init_dists)
print(init_angles)
adjusted_dists = sqrt_transformed_dist(init_dists)
adjusted_azimuths = get_adjusted_azimuth(init_angles)
print(adjusted_dists)
print(adjusted_azimuths)

adjusted_coords = adjusted(CoorList, adjusted_dists, adjusted_azimuths)
print(adjusted_coords)
draw_map(adjusted_coords)
