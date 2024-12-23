
# -*- coding: utf-8 -*-

import requests
from PIL import Image, ImageDraw, ImageFont
import os
import json
import math
import glob
import numpy as np
import math
import sys

id = 165024096
check_rpm = 12000
direction = 'z'

# {车号}_{区域机台号}_{机台锭号}_{上/下}_{转速}_{月日}_req.json
svr_reqs_files = {'6994f9e2d5df4e6bb4bee4f5e843a3e3_1_0_42': '01_03060_42_down_12000_1024_req.json',
                  '8094605d081648f5b6066df62eb2d12d_1_0_42': '01_03060_42_down_12000_1024_req.json',
                  'a1e8723108dc4c898fb271b7a4594161_1_0_56': '01_03068_56_down_12000_1024_req.json',
                  'e2b56fb6208e465b966a1f35fc7995e5_1_0_01': '01_03093_01_down_12000_1024_req.json',
                  '5d3816f7784240e0ab1b017b221ce87c_2_0_22': '01_03090_22_down_12000_1024_req.json',
                  '5d3816f7784240e0ab1b017b221ce87c_2_0_08': '01_03090_08_down_12000_1024_req.json',
                  '6c3110193bb440298a2cb66f3595d459_2_0_22': '01_03090_22_down_12000_1024_req.json',
                  'a47fa9e5d6964114bc511dfdcf6843d9_1_0_08': '01_03090_08_down_12000_1024_req.json',
                  '64579b6ca29347168363d52471ccc901_1_0_08': '01_03090_08_down_12000_1024_req.json',
                  'a040c27c0ce94b949abc29d4fd4494f9_1_0_21': '05_c9166_21_up_11000_1025_req.json',
                  '34f92c4663d245ae829d0171b61c7f5e_1_0_135': '03_02070_135_down_12000_1028.json',
                  'dc127c59d01a40208700daf6f7ac1035_1_0': '03_02069_84_down_12000_1029.json',
                  'e055fe27c4114358a7342239244e21a6_1_0': '03_03004_98_up_1030_req.json',
                  'daff1eb0f3274315a36d6ac25fb7d743_1_0': '02_03007_73_down_1030_req.json',
                  'a49223bbb4d14865bb6af0b3ae9699a4_1_0': '01_03090_97_down_12000_1031.json',
                  'aa91de1ee1464514838c172d3a873db8_1_0': '01_03065_121_down_1031_req.json',
                  '7563f6a3228e44c9a47254b51cac48e5_1_0': '02_03025_81_down_1031_req.json',
                  '47a0471386bc4f61b97beaa69195cbba_1_0': '05_c09171_80_down_1011_req.json',
                  'a49a5c4f12a5491e9922ea5ff16173a2_1_0': '05_c09209_122_up_11000_1106_req.json',
                  '477d219c71164259a6e3a194a0a4279f_1_0': '05_c09209_063_down_11000_1106_req.json',
                  '6beab798b2ba46ff95d0ddcd5617319d_1_0': '05_c09209_061_down_11000_1106_req.json',
                  '2625287b94c344368fbec975ab855959_2_0': '05_c09209_017_down_11200_1106_req.json',
                  '029dc5965f0b47d990a394d6d6dfdc2a_1_0': '05_c09209_127_down_11250_1106_req.json',
                  '029dc5965f0b47d990a394d6d6dfdc2a_1_0': '05_c09209_126_down_11250_1106_req.json',
                  '8b1830486d0c4e7caaaa4014fc058f1b_1_0': '05_c09209_64_up_11250_1106_req.json',
                  '8b1830486d0c4e7caaaa4014fc058f1b_1_0': '05_c09209_52_up_11250_1106_req.json',
                  '97822fdfda8e4f41a3e491b993a8995b_1_0': '05_c09209_03_down_11250_1108_req.json',
                  '9726576607524afeb37c689505a7227a_1_0': '05_c09207_117_up_11250_1108_req.json',
                  '8380710b21044c3e95f623ff79b5ba1f_1_0': '05_c09203_117_up_11250_1108_req.json',
                  id: 'temp_req.json'}
batch_no_logs = ['6c70322653bc438caa089103e9eb683e',
                 '407247cdaa4443579403a996b444ad3c',
                 'c3a57d677d1e43c5ad62a177692ddce7',
                 'd9df68938b4544ed991519ccf6d4ff2c']

local_batch_no = batch_no_logs[3]
svr_batch_no = 'c74bbf00356940d99c19779e2f41c92d_1_0'
img_prefix = 'cup_'
ratios = [0.529, 0.529]  # [0.519, 0.523]
ratio = ratios[1]
cache_path = "cache"
temp_path = os.path.join(cache_path, 'temp')


def theil(x, y):
    from sklearn.linear_model import TheilSenRegressor
    # 创建泰尔森回归模型
    model = TheilSenRegressor(max_iter=1000, random_state=0)
    # 训练模型
    model.fit(x[:, np.newaxis], y)
    # 获取回归线的斜率和截距
    slope = model.coef_[0]
    # median = np.median(x)
    # print(y, median)
    return slope


def show_theil(x, y):
    if len(x) < 3:
        return
    import matplotlib.pyplot as plt
    from sklearn.linear_model import TheilSenRegressor
    # 创建泰尔森回归模型
    model = TheilSenRegressor(max_iter=1000, random_state=0)
    # 训练模型
    model.fit(x[:, np.newaxis], y)
    # 获取回归线的斜率和截距
    slope = model.coef_[0]
    plt.text(10, 10, f'{slope}')
    intercept = model.intercept_
    # 绘制数据点
    plt.scatter(x, y, color='blue', label='Data points')
    for i in range(len(x)):
        plt.text(x[i]+0.2, y[i], f'{y[i]:.2f}')
    # 绘制回归线
    x_line = np.linspace(min(x), max(x), 100)
    y_line = slope * x_line + intercept
    plt.plot(x_line, y_line, color='red', label='Theil-Sen regression line')
    # 添加图例
    plt.legend()
    # 显示图表
    plt.show()


def draw_degree(x, y, mid_x, font, draw, bottom):
    if len(x) <= 2:
        return
    rpm = comp_rpm(np.array(x), np.array(y))
    coord_text = f"o_rpm:{int(rpm)}"
    bottom += 20
    draw.text((mid_x, bottom), coord_text,
              fill='yellow', font=font, stroke_fill='black', stroke_width=4)
    # 静态转速误差
    coord_text = f"r_rpm:{int(rpm)}"
    bottom += 20
    draw.text((mid_x, bottom), coord_text,
              fill='yellow', font=font, stroke_fill='black', stroke_width=4)


def read_req_cups(file_name, id):
    # JSON数据
    with open(os.path.join('./testdata', file_name), 'r', encoding='utf-8') as file:
        data = json.load(file)
    cups = {}
    result = {'img': list()}
    # nos = svr_batch_no.split('_')
    # if len(nos) > 3:
    #     batch_no = "_".join(nos[:-1])
    # else:
    #     batch_no = svr_batch_no
    # camera_name = 'Cam03'
    # if '_down_' in file_name:
    #     camera_name = 'Cam04'

    for item in data['data']['items']:
        if item['id'] != id:
            continue
        cups = item
    for cup in cups['itemImgJson']:
        img = {}
        img['url'] = cup['url'].split('/')[-1]
        img['box'] = list()
        if len(cup['list']) > 0:
            for boxi in cup['list']:
                box = {}
                box['left'] = boxi['x']
                box['top'] = boxi['y']
                box['width'] = boxi['width']
                box['height'] = boxi['height']
                box['label'] = boxi['label']
                img['box'].append(box)
        result['img'].append(img)
    return result


def read_degree(id):
    x = list()
    y = list()

    # JSON数据
    file_name = id + '_degree.json'
    full_path = os.path.join(r'.\testdata', file_name)
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for info in data['degreeInfo']:
        degree = info['degree']
        if degree == 9999:
            x = list()
            y = list()
            show_rpm(x, y)
            continue
        y.append(degree)
        x.append(info['frameId'])


def show_rpm(degrees: list[float], frames: list[float]):
    x = list()
    y = list()
    for i, d in enumerate(degrees):
        if d == -1:
            comp_rpm(x, y)
            show_theil(np.array(x), np.array(y))
            x = list()
            y = list()
            continue
        y.append(d)
        x.append(frames[i])
    if len(x) > 0:
        comp_rpm(x, y)
        show_theil(np.array(x), np.array(y))
    pass


def comp_rpm(x: list[int], y: list[float]) -> float:
    if len(x) < 3:
        return -1
    degree_per_frame = theil(np.array(x), np.array(y))
    s_per_frame = 1 / (check_rpm / 60 / 4)
    rpm = abs(degree_per_frame / s_per_frame * 60 / 360)
    result = comp_direction(rpm, degree_per_frame)
    print(
        f'测量频率：{check_rpm} 锭杯捻向：{direction} 测量结果：{result} 转速差：{rpm} 每帧角度：{degree_per_frame}')
    return result


def comp_direction(rpm, degree_per_frame):
    if 'z' in direction:
        # rpm += 7
        result = check_rpm + (rpm if degree_per_frame > 0 else -rpm)
    else:
        # rpm -= 7
        result = check_rpm + (-rpm if degree_per_frame > 0 else rpm)
    return round(result, 1)


def read_cup(id):
    # JSON数据
    file_name = id + '_cup.json'
    with open(os.path.join('./testdata', file_name), 'r') as file:
        data = json.load(file)
    return data

def comp_cups2(data, name):
    x = list()
    y = list()

    # 确保有一个目录来保存下
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    counter = 0
    for image_info in data['img']:
        counter += 1
        url = 'https://gemi-mes.oss-cn-hangzhou.aliyuncs.com/d/woven/robot-yb-c9-1/robot/twister/yarnpic/' + \
            image_info['url']
        image_path = os.path.join(cache_path, f'original_{counter:03d}.jpg')
        if not os.path.exists(image_path):
            response = requests.get(url)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
            else:
                exit(-1)

        # 打开图片
        img = Image.open(image_path)
        # 如果图片是黑白的，转换为RGB
        if img.mode == 'L':
            img = img.convert('RGB')
        # draw = ImageDraw.Draw(Image.new('RGB', (400, 300), color = (255, 255, 255)))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 20)

        spindle_mid_x = 0
        spindle_bottom_width = 0
        spindle_bottom_left = 0
        left = 0
        top = 0
        right = 0
        bottom = 0
        mid_x = 0
        if len(image_info['box']) < 2:
            draw_degree(x, y, mid_x, font, draw, bottom)
            show_theil(np.array(x), np.array(y))
            x = list()
            y = list()
            pass
        # 绘制矩形框
        for box in image_info['box']:
            if box['label'] != 0 and box['label'] != 1:
                lefts = box['left']
                tops = box['top']
                rights = left + box['width']
                bottoms = top + box['height']
                draw.rectangle(((lefts, tops), (rights, bottoms)),
                               outline='white', width=1)
                continue
            left = box['left']
            top = box['top']
            right = left + box['width']
            bottom = top + box['height']
            # 计算垂直线的x坐标
            mid_x = left + box['width'] / 2
            # 绘制垂直线
            draw.line(((mid_x, top - 50), (mid_x, bottom + 50)),
                      fill='red', width=1)
            if box['label'] == 0:
                draw.rectangle(((left, top), (right, bottom)),
                               outline='white', width=1)
                spindle_mid_x = mid_x
                # new_height_offset = (box['height'] - box['height'] * ratio)
                new_width_offset = (box['width'] - box['width'] * ratio) / 2
                left += new_width_offset
                right -= new_width_offset
                top = bottom - 45
                spindle_bottom_width = box['width'] * ratio
                spindle_bottom_left = spindle_mid_x - spindle_bottom_width/2
                draw.line(((left, top), (right, top)), fill='green', width=6)
                coord_text = f"width:{spindle_bottom_width}"
                draw.text((left, top - 25), coord_text,
                          fill='yellow', font=font, stroke_fill='black', stroke_width=4)
            else:
                draw.rectangle(((left, top), (right, bottom)),
                               outline='white', width=1)
                coord_text = f"mid_x:{mid_x - spindle_mid_x}"
                bottom += 50
                draw.text((mid_x, bottom), coord_text,
                          fill='yellow', font=font, stroke_fill='black', stroke_width=4)
                radian = (mid_x-spindle_bottom_left)/spindle_bottom_width   
                if radian > 1:
                    radian = 1
                elif radian < -1:
                    radian = -1
                degree = 180-math.degrees(math.asin(radian))*2
                coord_text = f"degree:{round(degree, 3)}"
                bottom += 20
                draw.text((mid_x, bottom), coord_text,
                          fill='yellow', font=font, stroke_fill='black', stroke_width=4)
                # if degree > 130 or degree < 50:
                #     continue
                y.append(degree)
                x.append(counter)

                # if len(x) == 5:
                #     y.append(58.73837580853305)
                #     x.append(6)
                draw_degree(x, y, mid_x, font, draw, bottom)

        # 保存绘制后的图片
        output_path = os.path.join(
            temp_path, f'{img_prefix}{counter:02d}_{name}.jpg')
        img.save(output_path)

    show_theil(np.array(x), np.array(y))
    print("图片下载和绘制完成。")

def comp_cups(data, name):
    x = list()
    y = list()

    # 确保有一个目录来保存下
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    counter = 0
    for image_info in data['img']:
        counter += 1
        url = 'https://gemi-mes.oss-cn-hangzhou.aliyuncs.com/d/woven/robot-yb-c9-1/robot/twister/yarnpic/' + \
            image_info['url']
        image_path = os.path.join(cache_path, f'original_{counter:03d}.jpg')
        if not os.path.exists(image_path):
            response = requests.get(url)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
            else:
                exit(-1)

        # 打开图片
        img = Image.open(image_path)
        # 如果图片是黑白的，转换为RGB
        if img.mode == 'L':
            img = img.convert('RGB')
        # draw = ImageDraw.Draw(Image.new('RGB', (400, 300), color = (255, 255, 255)))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 20)

        spindle_mid_x = 0
        spindle_bottom_width = 0
        spindle_bottom_left = 0
        left = 0
        top = 0
        right = 0
        bottom = 0
        mid_x = 0
        if len(image_info['box']) < 2:
            draw_degree(x, y, mid_x, font, draw, bottom)
            show_theil(np.array(x), np.array(y))
            x = list()
            y = list()
            pass
        # 绘制矩形框
        for box in image_info['box']:
            if box['label'] != 0 and box['label'] != 1:
                lefts = box['left']
                tops = box['top']
                rights = left + box['width']
                bottoms = top + box['height']
                draw.rectangle(((lefts, tops), (rights, bottoms)),
                               outline='white', width=1)
                continue
            left = box['left']
            top = box['top']
            right = left + box['width']
            bottom = top + box['height']
            # 计算垂直线的x坐标
            mid_x = left + box['width'] / 2
            # 绘制垂直线
            draw.line(((mid_x, top - 50), (mid_x, bottom + 50)),
                      fill='red', width=1)
            if box['label'] == 0:
                draw.rectangle(((left, top), (right, bottom)),
                               outline='white', width=1)
                spindle_mid_x = mid_x
                # new_height_offset = (box['height'] - box['height'] * ratio)
                new_width_offset = (box['width'] - box['width'] * ratio) / 2
                left += new_width_offset
                right -= new_width_offset
                top = bottom - 45
                spindle_bottom_width = box['width'] * ratio
                spindle_bottom_left = spindle_mid_x - spindle_bottom_width/2
                draw.line(((left, top), (right, top)), fill='green', width=6)
                coord_text = f"width:{spindle_bottom_width}"
                draw.text((left, top - 25), coord_text,
                          fill='yellow', font=font, stroke_fill='black', stroke_width=4)
            else:
                draw.rectangle(((left, top), (right, bottom)),
                               outline='white', width=1)
                coord_text = f"mid_x:{mid_x - spindle_mid_x}"
                bottom += 50
                draw.text((mid_x, bottom), coord_text,
                          fill='yellow', font=font, stroke_fill='black', stroke_width=4)
                radian = (mid_x - spindle_mid_x)/(spindle_bottom_width/2)
                if radian > 1:
                    radian = 1
                elif radian < -1:
                    radian = -1
                degree = math.degrees(math.acos(radian))
                coord_text = f"degree:{round(degree, 3)}"
                bottom += 20
                draw.text((mid_x, bottom), coord_text,
                          fill='yellow', font=font, stroke_fill='black', stroke_width=4)
                # if degree > 130 or degree < 50:
                #     continue
                y.append(degree)
                x.append(counter)

                # if len(x) == 5:
                #     y.append(58.73837580853305)
                #     x.append(6)
                draw_degree(x, y, mid_x, font, draw, bottom)

        # 保存绘制后的图片
        output_path = os.path.join(
            temp_path, f'{img_prefix}{counter:02d}_{name}.jpg')
        img.save(output_path)

    show_theil(np.array(x), np.array(y))
    print("图片下载和绘制完成。")


def init_output_folder():
    if os.path.exists(temp_path):
        # os.removedirs(temp_path)
        pattern = f'{os.path.join(cache_path, "*.jpg")}'
        for file_path in glob.glob(pattern):
            os.remove(file_path)
        pattern = f'{os.path.join(temp_path, "*.jpg")}'
        for file_path in glob.glob(pattern):
            os.remove(file_path)
    else:
        os.mkdir(temp_path)


# 非同频增量： 100 RPM
# 下采样： 100/4 = 25 RPM
# 每秒转动圈： 100/4/60 = 0.4166666667 r/s
# 每毫秒转动圈： 100/4/60/1000 = 0.0004166667 ms/r

# 频率： 11100 RPM
# 下采样： 11100/4 = 2775 RPM
# 帧率： 11100/4/60 = 46.25 fps
# 帧间隔： 1000/(11100/240) = 21.6216216216 ms

# 每帧圈增量： 100/240/1000 * 1000/(11100/240) = 0.0090090090 f/r
# 每帧角度增量： 100/240/1000 * 1000/(11100/240) * 360 = 3.2432432432

def rpm_degree_per_ms(true_rpm: int, detect_rpm: int, downsampling_num: int):
    downsampling = true_rpm / downsampling_num
    round_per_second = downsampling / 60
    print('下4采样：')
    print(f'每秒旋圈数: {round_per_second}')
    ms_per_round = 1000 / round_per_second
    print(f'每圈所需ms: {ms_per_round}')
    round_per_ms = round_per_second / 1000
    print(f'每ms所转圈数: {round_per_ms}')

    fps = (detect_rpm)/downsampling_num/60
    print(f'检测时帧率: {fps}')
    frame_interval_ms = 1000/(fps)
    print(f'检测时帧间隔ms: {frame_interval_ms}')
    inc_degree = abs(frame_interval_ms * round_per_ms * 360)
    print(f'每帧旋转角度: {inc_degree}')


def rpm_degree_per_frame(true_rpm: int, detect_rpm: int, downsampling_num: int):
    downsampling = true_rpm / downsampling_num
    round_per_second = downsampling / 60
    print('下4采样：')
    print(f'每秒旋圈数: {round_per_second}')
    angle_per_second = round_per_second * 360
    print(f'每秒旋转总角度: {angle_per_second}')

    fps = (detect_rpm)/downsampling_num/60
    print(f'检测时帧率: {fps}')
    frame_interval_ms = 1/(fps)
    print(f'检测时帧间隔s: {frame_interval_ms}')
    inc_degree = abs(frame_interval_ms * angle_per_second-360)
    # 下采样后，每帧之间会有downsampling_num次的旋转增量
    total_degree = inc_degree*downsampling_num
    print(f'每帧旋转角度: {total_degree}')
    return (total_degree, fps)


def hole_visibility_per_spindle_area(spindle_area_width: float, speed: float, true_rpm: int, detect_rpm: int, downsampling_num: int):
    visibility_time_s = spindle_area_width / speed
    print(f'锭子可观测时间: {visibility_time_s}')
    res = rpm_degree_per_frame(true_rpm, detect_rpm, downsampling_num)
    inc_degree = res[0]
    fps = res[1]
    frames = visibility_time_s / (1/fps)
    print(f'总可见帧数{frames}')
    total_degree = frames * inc_degree
    print(f'总可见角度{total_degree:.2f} 有效占比{total_degree/360:.2f}')


def verifyFrameAngleOverlimit(degrees: list[float], true_rpm: int, detect_rpm: int, downsampling_num: int):
    """
    是否大概率超过测定转速范围

    :param degrees: 角度列表，每个元素表示一帧的角度
    :return: 如果满足超过测定转速范围的条件则返回True，否则返回False
    """
    downsampling = true_rpm / downsampling_num
    round_per_second = downsampling / 60
    print('下4采样：')
    print(f'每秒旋圈数: {round_per_second}')
    angle_per_second = round_per_second * 360
    print(f'每秒旋转总角度: {angle_per_second}')

    fps = (detect_rpm)/downsampling_num/60
    print(f'检测时帧率: {fps}')
    frame_interval_ms = 1/(fps)
    print(f'检测时帧间隔s: {frame_interval_ms}')
    inc_degree = abs(frame_interval_ms * angle_per_second-360)
    # 下采样后，每帧之间会有downsampling_num次的旋转增量
    total_degree = inc_degree*downsampling_num
    print(f'每帧旋转角度: {total_degree}')

    # 每帧之间角度阈值(约相差±300RPM)
    limitDegree = total_degree
    prevDegree = 0.0
    overLimitTimes = 0
    totalHoleCouples = 0
    for i in range(len(degrees)):
        # 两帧角度计算
        if degrees[i] != -1 and prevDegree != -1:
            totalHoleCouples += 1
            degree = degrees[i] - prevDegree
            if not (math.fabs(degree) < limitDegree - 0.05):
                # 帧间最大旋转角度
                overLimitTimes += 1
        prevDegree = degrees[i]
    if totalHoleCouples < 1:
        return False
    overLimitPercent = (overLimitTimes / totalHoleCouples + 0.005) * 100
    if overLimitPercent >= 50:
        # 旋转角度大于阈值占比大于50%，认为该锭速异常
        print("over limit: ", overLimitPercent)
        return True
    return False


def inc_degree_to_rpm(degree_per_frame: float):
    s_per_frame = 1 / (check_rpm / 60 / 4)
    # 形式改变，避免分母为0：rpm = 60 / (360 / degree_per_frame * s_per_frame)
    rpm = 60 / 360 * degree_per_frame / s_per_frame
    result = comp_direction(rpm, s_per_frame)
    print(
        f'每帧角度差{degree_per_frame}° 测量频率{check_rpm} 捻向{direction} 总转速差{rpm} 检测结果{result}')

# 读取角度文件进行计算
# read_degree(local_batch_no)
# hole_visibility_per_spindle_area(0.18, 0.45, 12100, 12200, 4)


# # 计算转速与角度的关系
# -542
# rpm_degree_per_frame(12458, 13000, 4)
# -480
# rpm_degree_per_frame(11500, 12000, 4)
# rpm_degree_per_frame(11550, 12050, 4)
# rpm_degree_per_frame(10000, 12000, 4)
# rpm_degree_per_frame(11000, 12000, 4)
# rpm_degree_per_frame(11500, 12000, 4)
# rpm_degree_per_frame(11600, 12000, 4)
# rpm_degree_per_frame(11700, 12000, 4)

# rpm_degree_per_frame(10500, 11000, 4)
# rpm_degree_per_frame(10600, 11000, 4)
# rpm_degree_per_frame(10700, 11000, 4)

# -440
# rpm_degree_per_frame(10900, 11000, 4)

rpm_degree_per_frame(8850, 9000, 4)

# # 读取apass的请求进行计算
# init_output_folder()
# comp_cups(read_req_cups(
#     svr_reqs_files[id], id), id)

# diameter = int(380*0.5294)
# radius = int(diameter / 2)
# for r in range(0, diameter):
#     x = (r-radius)/radius
#     res = math.degrees(math.acos(x))
#     print(f'角度：{res}° 临边：{r}')
#     inc_degree_to_rpm(res)

# # 读取apass的文本
# degree_str = "33.55/89.11/140.55"
# degree = [float(item) for item in str.split(degree_str, "/")]
# frames = range(len(degree))
# show_rpm(degree, frames)


# print(verifyFrameAngleOverlimit(degree, 11000, 11300, 4))

# radius = 380*0.5294 / 2
# x = (radius-1)/radius
# res = math.degrees(math.acos(x))
# print(f'角度：{res}° 半径：{radius}')
# inc_degree_to_rpm(res)

# x = (radius)/radius
# res = math.degrees(math.acos(x))
# print(f'角度：{res}° 半径：{radius}')
# inc_degree_to_rpm(res)
