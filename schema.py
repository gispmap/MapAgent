import json
import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import re
import random
import matplotlib.image as mpimg
import matplotlib.offsetbox as offsetbox
from pylab import mpl
from pyproj import Transformer

mpl.rcParams["font.sans-serif"] = ["SimHei"]   # 设置显示中文字体
mpl.rcParams["axes.unicode_minus"] = False   # 设置正常显示符号


def calculate_azimuth(lat1, lon1, lat2, lon2):
    delta_x = lon2 - lon1
    delta_y = lat2 - lat1
    theta = math.degrees(math.atan2(delta_y, delta_x))
    return theta


def calculate_distance(lat1, lon1, lat2, lon2):
    # 使用Haversine公式计算地球表面两点间的距离
    r = 6371.0  # 地球半径，单位为公里

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = r * c * 1000  # 转换为米
    distance = round(distance, 2)
    return distance


def calculate_new_coordinates(lat1, lon1, distance, azimuth):
    # 将方位角从度转换为弧度
    azimuth = math.radians(azimuth)
    cos_azimuth = round(math.cos(azimuth), 2)
    sin_azimuth = round(math.sin(azimuth), 2)

    # 计算距离转换后的经纬度差值
    delta_x = distance * cos_azimuth
    delta_x = round(delta_x, 2)
    delta_y = distance * sin_azimuth
    delta_y = round(delta_y, 2)

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


# 对数变化距离
def log_transformed_dist(distancelist):
    # 指定缩放范围
    min_target = 1000
    max_target = 5000
    # 对数变换然后缩放
    log_transformed = np.log1p(distancelist)  # log1p用于避免log(0)问题
    log_min = min(log_transformed)
    log_max = max(log_transformed)
    log_scaled_distances = [(x - log_min) / (log_max - log_min) * (max_target - min_target) + min_target for x in
                            log_transformed]

    # 四舍五入取整
    log_scaled_distances = [int(round(x)) for x in log_scaled_distances]
    return log_scaled_distances


def sqrt_transformed_dist(distancelist):
    # 指定缩放范围
    min_target = 4000
    max_target = 8000
    # 平方根变换
    sqrt_transformed = np.sqrt(distancelist)
    sqrt_min = min(sqrt_transformed)
    sqrt_max = max(sqrt_transformed)
    sqrt_scaled_distances = [(x - sqrt_min) / (sqrt_max - sqrt_min) * (max_target - min_target) + min_target for x in
                             sqrt_transformed]

    # 四舍五入取整
    log_scaled_distances = [int(round(x)) for x in sqrt_scaled_distances]
    return log_scaled_distances


def init_dist_azi(pointlist):
    # 初始距离列表
    dist = []
    # 初始角度列表
    azimuth = []
    for i in range(len(pointlist) - 1):
        lat1, lon1 = pointlist[i]
        lat2, lon2 = pointlist[i + 1]
        # 计算初始方位角和距离
        initial_azimuth = calculate_azimuth(lat1, lon1, lat2, lon2)
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        azimuth.append(initial_azimuth)
        dist.append(distance)
    return dist, azimuth


def adjusted_coord(pointlist, adjusted_dists, adjusted_azimuths):
    # 新坐标
    adjusted_coords = [pointlist[0]]

    # 根据调整后的方位角和距离计算新的坐标
    for i in range(len(pointlist) - 1):
        new_lat1, new_lon1 = adjusted_coords[i]
        # 根据调整后的方位角和距离计算新的坐标
        new_lat2, new_lon2 = calculate_new_coordinates(new_lat1, new_lon1, adjusted_dists[i], adjusted_azimuths[i])
        adjusted_coords.append([new_lat2, new_lon2])
    return adjusted_coords


def mercator_to_pixels(mercator_coords, img):
    # 计算墨卡托坐标的范围
    x_min = min(coord[0] for coord in mercator_coords) - 1000
    x_max = max(coord[0] for coord in mercator_coords) + 1000
    y_min = min(coord[1] for coord in mercator_coords) - 1000
    y_max = max(coord[1] for coord in mercator_coords) + 1000

    x_pixels = []
    y_pixels = []
    for i in range(len(mercator_coords)):
        x_pixel = (mercator_coords[i][0] - x_min) / (x_max - x_min) * img.shape[1]
        y_pixel = (y_max - mercator_coords[i][1]) / (y_max - y_min) * img.shape[0]
        x_pixels.append(x_pixel)
        y_pixels.append(y_pixel)
    return x_pixels, y_pixels


def transform_crs(pointlist, crs_from="epsg:4326", crs_to="epsg:3857"):
    # 初始化 Transformer
    transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)

    # 将经纬度转换为墨卡托投影坐标
    mercator_coords = [transformer.transform(lon, lat) for lat, lon in pointlist]
    return mercator_coords


def get_json(strjson):
    strjson = re.sub(r'```|json', '', strjson)  # 正则表达式
    data = json.loads(strjson)
    return data


def point_symbolic(ax, x, y, point_size=100, symbols_path=None):
    if symbols_path:
        image_path = symbols_path  # 替换为自定义点符号的实际路径
        img = mpimg.imread(image_path)
    # 原始圆点的大小
        dot_size = point_size  # 例如，原圆点的面积为100平方点
        dot_radius = np.sqrt(dot_size / np.pi)  # 计算圆点的半径
        # 自定义符号的尺寸
        icon_size = 2 * dot_radius  # 使自定义符号的大小与原圆点相匹配
        # 创建 OffsetImage 对象
        imagebox = offsetbox.OffsetImage(img, zoom=icon_size / img.shape[0], resample=True)
        # 用自定义符号替换散点图
        for (i, j) in zip(x, y):
            ab = offsetbox.AnnotationBbox(imagebox, (i, j), frameon=False, pad=0.5, bboxprops=dict(zorder=50))
            ax.add_artist(ab)
    else:
        return


def draw_point(ax, x, y, symbols_path=None, s=100, c='blue'):
    if not symbols_path:
        ax.scatter(x, y, color=c, s=s)
    else:
        point_symbolic(ax, x, y, s, symbols_path=symbols_path)
    return


def trans_backgroud(ax, adjusted_coords, bg_img_path=None):
    if bg_img_path:
        # 读入图片
        bg_img = mpimg.imread(bg_img_path)
        ax.imshow(bg_img)
        # 将墨卡托坐标转换为像素坐标
        mercator_coords = transform_crs(adjusted_coords, crs_from="epsg:4326", crs_to="epsg:3857")
        x, y = mercator_to_pixels(mercator_coords, bg_img)
        return x, y
    else:
        x = [lon for lat, lon in adjusted_coords]
        y = [lat for lat, lon in adjusted_coords]
        return x, y


def draw_subfig(fig, gs, x, y, routelist, namelist, colors):
    routenum = len(routelist)
    # 为每个副图添加数据和标题
    n = 0
    for i in range(routenum):
        num = len(routelist[i])
        ax_sub = fig.add_subplot(gs[2, i])
        x_sub, y_sub = x[n:(n + num)], y[n:(n + num)]
        sub_name = namelist[n:(n + num)]
        ax_sub.scatter(x_sub, y_sub, color=colors[i])
        ax_sub.plot(x_sub, y_sub, color=colors[i], linestyle='-', label=f'day{i + 1}')
        # 标注点号
        for index in range(len(x_sub)):
            lon = x_sub[index]
            lat = y_sub[index]
            ax_sub.annotate(
                f'{sub_name[index]}',
                (lon, lat),
                textcoords="offset points",
                xytext=(-5, -20),
                ha='left',
                fontsize=12, color=colors[i])
        ax_sub.set_title(f'Route Of Day{i + 1}')
        ax_sub.set_xticks([])
        ax_sub.set_yticks([])
        n += num


def draw_map(adjusted_coords, routelist, maptitle, namelist,  symbols_path=None, bg_img_path=None, subfig=False):
    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'brown', 'gray', 'black']
    y_min = min(coord[0] for coord in adjusted_coords) - 0.04
    y_max = max(coord[0] for coord in adjusted_coords) + 0.04
    x_min = min(coord[1] for coord in adjusted_coords) - 0.04
    x_max = max(coord[1] for coord in adjusted_coords) + 0.04
    # 创建绘图
    route_num = len(routelist)
    fig = plt.figure(figsize=(15, 8))
    gs = gridspec.GridSpec(3, route_num, height_ratios=[2, 1, 1])
    ax_main = fig.add_subplot(gs[0:2, :])
    # 添加背景
    x, y = trans_backgroud(ax_main, adjusted_coords, bg_img_path=bg_img_path)
    # 绘制点
    draw_point(ax_main, x, y, symbols_path=symbols_path, s=70, c='blue')

    # 标注点号
    for index in range(len(x)):
        lon = x[index]
        lat = y[index]
        ax_main.annotate(
            f'{namelist[index]}',
            (lon, lat),
            textcoords="offset points",
            xytext=(5, 5),
            ha='left',
            fontsize=8,
            color='black')

    # 绘制调整后的线段和标注
    j = 0
    for i in range(route_num):
        # random_integer = random.randint(0, 9)
        num = len(routelist[i])
        route_x = x[j:(j + 1 + num)]
        route_y = y[j:(j + 1 + num)]
        ax_main.plot(route_x, route_y, color=colors[i], linestyle='-', label=f'day{i+1}')
        j += num

    ax_main.set_title(maptitle)
    ax_main.set_xticks([])  # 隐藏x轴刻度
    ax_main.set_yticks([])  # 隐藏y轴刻度
    ax_main.set_xlim(x_min, x_max)
    ax_main.set_ylim(y_min, y_max)
    # ax_main.set_aspect('equal')
    ax_main.legend()
    # ax.axis('off')  #隐藏坐标轴
    if subfig:
        draw_subfig(fig, gs, x, y, routelist, namelist, colors)

    # 自动调整布局
    plt.tight_layout()
    plt.show()


def final(pointlist, routelist, maptitle, namelist, symbols_path=None, bg_img_path=None, subfig=False):
    init_dists, init_angles = init_dist_azi(pointlist)
    print(init_dists)
    print(init_angles)
    adjusted_dists = sqrt_transformed_dist(init_dists)
    adjusted_azimuths = get_adjusted_azimuth(init_angles)
    print(adjusted_dists)
    print(adjusted_azimuths)
    adjusted_coords = adjusted_coord(pointlist, adjusted_dists, adjusted_azimuths)
    print(adjusted_coords)
    draw_map(adjusted_coords, routelist, maptitle, namelist, symbols_path=symbols_path, bg_img_path=bg_img_path, subfig=subfig)


data1 = '```json\n{\n    "制图区域": "北京",\n    "地图类型": "旅游地图",\n    "制图信息": {\n        "NameList": [\n            "天安门广场",\n            "故宫",\n            "王府井",\n            "南锣鼓巷",\n            "北海公园",\n            "颐和园",\n            "清华大学",\n            "圆明园"\n        ],\n        "CoorList": [\n            [39.908719, 116.397479],\n            [39.916345, 116.397155],\n            [39.912469, 116.403909],\n            [39.933176, 116.407358],\n            [39.924091, 116.396907],\n            [39.999976, 116.275461],\n            [40.002189, 116.326503],\n            [40.008152, 116.304508]\n        ],\n        "Tickets": [\n            "免费",\n            "60元",\n            "免费",\n            "免费",\n            "20元",\n            "30元",\n            "免费",\n            "10元"\n        ],\n        "RouteList": [\n            ["天安门广场", "故宫", "王府井"],\n            ["南锣鼓巷", "北海公园"],\n            ["颐和园", "清华大学", "圆明园"]\n        ],\n        "TourTime": {\n            "day1": ["2h", "4h", "2h"],\n            "day2": ["3h", "3h"],\n            "day3": ["3h", "2h", "3h"]\n        },\n        "Transportation": {\n            "day1": ["步行1公里", "步行500米"],\n            "day2": ["步行1.5公里"],\n            "day3": ["开车或打车15公里", "步行2公里"]\n        },\n        "Description": "第一天游览天安门广场、故宫和王府井。第二天游览南锣鼓巷和北海公园。第三天游览颐和园、清华大学和圆明园。"\n    }\n}\n```'
data2 = '```json\n{\n    "制图区域": "北京",\n    "地图类型": "旅游地图",\n    "制图信息": {\n        "NameList": [\n            "天安门广场",\n            "故宫博物院",\n            "景山公园",\n            "北海公园",\n            "王府井商业街",\n            "颐和园",\n            "圆明园",\n            "北京大学",\n            "清华大学",\n            "北京动物园",\n            "长城",\n            "十三陵",\n            "鸟巢",\n            "水立方"\n        ],\n        "CoorList": [\n            [39.908722, 116.397499],\n            [39.916345, 116.397155],\n            [39.929986, 116.394547],\n            [39.924399, 116.389155],\n            [39.912586, 116.409667],\n            [39.999975, 116.273057],\n            [40.007978, 116.299293],\n            [39.998003, 116.317458],\n            [40.002217, 116.327391],\n            [39.938883, 116.333304],\n            [40.431908, 116.570374],\n            [40.253530, 116.144951],\n            [39.992079, 116.390501],\n            [39.992933, 116.396546]\n        ],\n        "Tickets": [\n            "免费",\n            "60元",\n            "2元",\n            "10元",\n            "免费",\n            "30元",\n            "10元",\n            "免费",\n            "免费",\n            "20元",\n            "40元",\n            "45元",\n            "50元",\n            "30元"\n        ],\n        "RouteList": [\n            [\n                "天安门广场",\n                "故宫博物院",\n                "景山公园",\n                "北海公园",\n                "王府井商业街"\n            ],\n            [\n                "颐和园",\n                "圆明园"\n            ],\n            [\n                "北京大学",\n                "清华大学",\n                "北京动物园"\n            ],\n            [\n                "长城",\n                "十三陵"\n            ],\n            [\n                "鸟巢",\n                "水立方"\n            ]\n        ],\n        "TourTime": {\n            "day1": [\n                "2h",\n                "3h",\n                "1.5h",\n                "2h",\n                "2h"\n            ],\n            "day2": [\n                "3h",\n                "2h"\n            ],\n            "day3": [\n                "2h",\n                "2h",\n                "3h"\n            ],\n            "day4": [\n                "3h",\n                "3h"\n            ],\n            "day5": [\n                "2h",\n                "2h"\n            ]\n        },\n        "Transportation": {\n            "day1": [\n                "步行1公里",\n                "步行1公里",\n                "步行2公里",\n                "步行1公里"\n            ],\n            "day2": [\n                "开车或打车5公里"\n            ],\n            "day3": [\n                "步行2公里",\n                "步行2公里"\n            ],\n            "day4": [\n                "开车或打车10公里"\n            ],\n            "day5": [\n                "步行2公里"\n            ]\n        },\n        "Description": "1. 第一天：天安门广场 - 故宫博物院 - 景山公园 - 北海公园 - 王府井商业街。上午游览天安门广场和故宫博物院，可在王府井商业街就餐和购物。2. 第二天：颐和园 - 圆明园。探索颐和园的美景，下午前往圆明园。3. 第三天：北京大学 - 清华大学 - 北京动物园。参观中国最著名的两所大学和北京动物园。4. 第四天：长城 - 十三陵。体验雄伟的长城和十三陵的历史文化。5. 第五天：鸟巢 - 水立方。参观2008年北京奥运会的场馆鸟巢和水立方。"\n    }\n}\n```'
data3 = '```json\n{\n    "制图区域": "北京市",\n    "地图类型": "旅游地图",\n    "制图信息": {\n        "NameList": [\n            "香山公园", \n            "古水北镇", \n            "明十三陵", \n            "颐和园", \n            "天安门广场", \n            "故宫", \n            "南锣鼓巷", \n            "王府井", \n            "鸟巢", \n            "798艺术区", \n            "北海公园"\n        ],\n        "CoorList": [\n            [39.990593, 116.188720],\n            [40.558875, 116.010622],\n            [40.253936, 116.233244],\n            [39.998353, 116.275489],\n            [39.908496, 116.397232],\n            [39.916344, 116.390800],\n            [39.933709, 116.408799],\n            [39.908778, 116.397502],\n            [39.992885, 116.396119],\n            [39.984347, 116.495674],\n            [39.928846, 116.381260]\n        ],\n        "Tickets" : [\n            "10元",\n            "150元",\n            "45元",\n            "30元",\n            "免费",\n            "60元",\n            "免费",\n            "免费",\n            "50元",\n            "免费",\n            "10元"\n        ],\n        "RouteList": [\n            ["天安门广场", "故宫", "南锣鼓巷", "王府井"],\n            ["香山公园", "颐和园", "鸟巢", "798艺术区"],\n            ["古水北镇", "明十三陵", "北海公园"]\n        ],\n        "TourTime": {\n            "day1": ["1h", "2h", "2h", "2h"],\n            "day2": ["3h", "3h", "2h", "2h"],\n            "day3": ["3h", "3h", "2h"]\n        },\n        "Transportation": {\n            "day1": ["步行0.5公里", "步行1公里", "步行1公里", "步行2公里"],\n            "day2": ["开车或打车10公里", "开车或打车12公里", "开车或打车15公里", "开车或打车10公里"],\n            "day3": ["开车或打车60公里", "开车或打车30公里", "开车或打车20公里"]\n        },\n        "Description": "第一天的旅游计划是游览天安门广场、故宫、南锣鼓巷和王府井，并步行游览这些景点。第二天，我们将参观香山公园、颐和园、鸟巢和798艺术区，可以选择开车或打车前往这些地方。第三天的旅游景点包括古水北镇和明十三陵，最后参观北海公园，可以选择开车或打车进行交通。"\n    }\n}\n```'
data4 = '{\n    "制图区域": "北京",\n    "地图类型": "旅游地图",\n    "制图信息": {\n        "NameList": [\n            "天安门广场", "毛主席纪念堂", "前门大街", "故宫", "什刹海", \n            "八达岭长城", "奥林匹克公园", "鸟巢", "水立方", \n            "颐和园", "圆明园", "天坛公园", "清华", "北京大学"\n        ],\n        "CoorList": [\n            [39.908722, 116.397499], [39.903640, 116.391500], [39.901245, 116.402970], [39.916345, 116.397155], [39.937500, 116.395370], \n            [40.359756, 116.020383], [40.007435, 116.397977], [39.992878, 116.391570], [39.999616, 116.397850], \n            [39.998267, 116.273039], [40.007847, 116.305451], [39.882222, 116.406622], [40.004103, 116.329160], [39.999929, 116.321783]\n        ],\n        "Tickets": [\n            "免费", "免费", "免费", "60元", "免费",\n            "40元", "免费", "免费", "免费", \n            "30元", "10元", "15元", "免费", "免费"\n        ],\n        "RouteList": [\n            ["天安门广场", "毛主席纪念堂", "前门大街", "故宫", "什刹海"],\n            ["八达岭长城", "奥林匹克公园", "鸟巢", "水立方"],\n            ["颐和园", "圆明园", "天坛公园", "清华", "北京大学"]\n        ],\n        "TourTime": {\n            "day1": ["1h", "1h", "1.5h", "3h", "2h"],\n            "day2": ["3h", "2h", "1h", "1h"],\n            "day3": ["3h", "2h", "2h", "1.5h", "1.5h"]\n        },\n        "Transportation": {\n            "day1": [\n                "步行0.3公里", "步行0.8公里", "开车或打车2.2公里", "开车或打车4.5公里"\n            ],\n            "day2": [\n                "开车或打车70公里", "开车或打车10公里", "步行0.5公里", "步行0.5公里"\n            ],\n            "day3": [\n                "开车或打车5.5公里", "开车或打车1.5公里", "开车或打车20公里", "开车或打车2公里"\n            ]\n        },\n        "Description": "Day1游览天安门广场、毛主席纪念堂、前门大街、故宫和什刹海。Day2参观八达岭长城、奥林匹克公园、鸟巢和水立方。Day3游览颐和园、圆明园、天坛公园、清华和北京大学。"\n    }\n}'
mydata = get_json(data1)
NameList = mydata['制图信息']['NameList']
route = mydata['制图信息']['RouteList']
point = mydata['制图信息']['CoorList']
print(point)
title = mydata['地图类型']
symbol_path = 'E:/Project/MapAgent/store/天坛.png'

bg_img_path = 'E:/Project/MapAgent/store/backgroundimg.png'
draw_map(point, route, title, NameList)

final(point, route, title, NameList)

