
# -*- coding: utf-8 -*-

import requests
from PIL import Image, ImageDraw, ImageFont
import os
import json
import math
import glob
import numpy as np
import sys

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
                  'daff1eb0f3274315a36d6ac25fb7d743_1_0': '02_03007_73_down_1030_req.json'}
batch_no_logs = ['6c70322653bc438caa089103e9eb683e',
                 '407247cdaa4443579403a996b444ad3c',
                 'c3a57d677d1e43c5ad62a177692ddce7']


local_batch_no = batch_no_logs[2]
svr_batch_no = 'daff1eb0f3274315a36d6ac25fb7d743_1_0'

check_rpm = 12200
img_prefix = 'cup_'
ratios = [0.519, 0.523]
ratio = ratios[1]
cache_path = "cache"
temp_path = os.path.join(cache_path, 'temp')


def theil(x, y):
    from sklearn.linear_model import TheilSenRegressor

    # 创建泰尔森回归模型
    model = TheilSenRegressor(random_state=0)

    # 训练模型
    model.fit(x[:, np.newaxis], y)

    # 获取回归线的斜率和截距
    slope = model.coef_[0]
    # median = np.median(x)
    # print(y, median)
    return slope


def show_theil(x, y):
    import matplotlib.pyplot as plt
    from sklearn.linear_model import TheilSenRegressor
    # 创建泰尔森回归模型
    model = TheilSenRegressor(random_state=0)
    # 训练模型
    model.fit(x[:, np.newaxis], y)
    # 获取回归线的斜率和截距
    slope = model.coef_[0]
    plt.text(0, 0, f'{slope}')
    intercept = model.intercept_
    # 绘制数据点
    plt.scatter(x, y, color='blue', label='Data points')
    # 绘制回归线
    x_line = np.linspace(min(x), max(x), 100)
    y_line = slope * x_line + intercept
    plt.plot(x_line, y_line, color='red', label='Theil-Sen regression line')
    # 添加图例
    plt.legend()
    # 显示图表
    plt.show()


def read_req_cups(file_name):
    # JSON数据
    with open(os.path.join('./testdata', file_name), 'r', encoding='utf-8') as file:
        data = json.load(file)
    cups = {}
    result = {'img': list()}
    nos = svr_batch_no.split('_')
    if len(nos) > 3:
        batch_no = "_".join(nos[:-1])
    else:
        batch_no = svr_batch_no
    camera_name = 'Cam03'
    if '_down_' in file_name:
        camera_name = 'Cam04'

    for item in data['data']['items']:
        if item['batch_no'] != batch_no or item['camera_no'] != camera_name:
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


def read_degree(local_batch_no):
    x = list()
    y = list()

    # JSON数据
    file_name = local_batch_no + '_degree.json'
    full_path = os.path.join(r'.\testdata', file_name)
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for info in data['degreeInfo']:
        degree = info['degree']
        if degree == 9999:
            continue
        y.append(degree)
        x.append(info['frameId'])

    slope = theil(np.array(x), np.array(y))
    s_per_frame = 1 / (check_rpm / 60 / 4)
    rpm = abs(slope / s_per_frame * 60 / 360)
    result = check_rpm - rpm
    result += -7 if slope > 0 else 0
    result = round(result, 1)
    show_theil(np.array(x), np.array(y))
    print(rpm, result)


def read_cup(local_batch_no):
    # JSON数据
    file_name = local_batch_no + '_cup.json'
    with open(os.path.join('./testdata', file_name), 'r') as file:
        data = json.load(file)
    return data


def comp_cups(data, name):
    x = list()
    y = list()

    # 确保有一个目录来保存下载的图片
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    counter = 0
    for image_info in data['img']:
        counter += 1
        url = 'https://gemi-mes.oss-cn-hangzhou.aliyuncs.com/d/woven/robot-yb-c9-1/robot/twister/yarnpic/' + \
            image_info['url']
        image_path = os.path.join(cache_path, url.split('/')[-1])
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
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 20)

        spindle_mid_x = 0
        ratio = 0.519
        spindle_bottom_width = 0
        # 绘制矩形框
        for box in image_info['box']:
            if box['label'] != 0 and box['label'] != 1:
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
                spindle_bottom_width = round(box['width'] * ratio, 1)
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

                radian = (mid_x - spindle_mid_x)/spindle_bottom_width*2
                if radian > 1:
                    radian = 1
                elif radian < -1:
                    radian = -1
                degree = math.degrees(math.acos(radian))
                coord_text = f"degree:{round(degree, 3)}"
                bottom += 20
                draw.text((mid_x, bottom), coord_text,
                          fill='yellow', font=font, stroke_fill='black', stroke_width=4)

                y.append(degree)
                x.append(counter)

                # if len(x) == 5:
                #     y.append(58.73837580853305)
                #     x.append(6)
                slope = theil(np.array(x), np.array(y))
                if len(x) > 2:
                    s_per_frame = 1 / (check_rpm / 60 / 4)
                    rpm = abs(slope / s_per_frame * 60 / 360)
                    coord_text = f"o_rpm:{int(rpm)}"
                    bottom += 20
                    draw.text((mid_x, bottom), coord_text,
                              fill='yellow', font=font, stroke_fill='black', stroke_width=4)
                    result = check_rpm - rpm
                    # 静态转速误差
                    result += -7 if slope > 0 else 7
                    coord_text = f"r_rpm:{int(result)}"
                    bottom += 20
                    draw.text((mid_x, bottom), coord_text,
                              fill='yellow', font=font, stroke_fill='black', stroke_width=4)

        # 保存绘制后的图片
        output_path = os.path.join(
            temp_path, f'{img_prefix}{counter:02d}_{name}.jpg')
        img.save(output_path)

    # 假设我们有一组数据
    show_theil(np.array(x), np.array(y))
    print("图片下载和绘制完成。")


def init_output_folder():
    if os.path.exists(temp_path):
        # os.removedirs(temp_path)
        pattern = f'{os.path.join(temp_path, img_prefix+"*")}'
        for file_path in glob.glob(pattern):
            os.remove(file_path)
    else:
        os.mkdir(temp_path)


# read_degree(local_batch_no)

init_output_folder()
comp_cups(read_req_cups(
    svr_reqs_files[svr_batch_no]), svr_reqs_files[svr_batch_no])
# read_cup(local_batch_no)
