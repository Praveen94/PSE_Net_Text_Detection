# -*- coding: utf-8 -*-
# @Time    : 2018/6/11 15:54
# @Author  : zhoujun
import torch
import shutil
import numpy as np
import config
import os
import cv2
import argparse

from tqdm import tqdm
from models import PSENet
from predict import Pytorch_model
from cal_recall.script import cal_recall_precison_f1
from utils import draw_bbox

torch.backends.cudnn.benchmark = True


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, default=None,
                        help='model_path')
    parser.add_argument('--data_path', type=str,
                        default=None, help='data_path')
    parser.add_argument('--gt_path', type=str, default=None,
                        help='gt_path')
    parser.add_argument('--save_path', type=str,
                        default=None, help='save_path')

    return parser.parse_args()



def main(model_path, backbone, scale, path, save_path, gpu_id):
    if os.path.exists(save_path):
        shutil.rmtree(save_path, ignore_errors=True)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_img_folder = os.path.join(save_path, 'img')
    if not os.path.exists(save_img_folder):
        os.makedirs(save_img_folder)
    save_txt_folder = os.path.join(save_path, 'result')
    if not os.path.exists(save_txt_folder):
        os.makedirs(save_txt_folder)
    img_paths = [os.path.join(path, x) for x in os.listdir(path)]
    net = PSENet(backbone=backbone, pretrained=False, result_num=config.n)
    model = Pytorch_model(model_path, net=net, scale=scale, gpu_id=gpu_id)
    total_frame = 0.0
    total_time = 0.0
    for img_path in tqdm(img_paths):
        img_name = os.path.basename(img_path).split('.')[0]
        save_name = os.path.join(save_txt_folder, 'res_' + img_name + '.txt')
        _, boxes_list, t = model.predict(img_path)
        total_frame += 1
        total_time += t
        # img = draw_bbox(img_path, boxes_list, color=(0, 0, 255))
        # cv2.imwrite(os.path.join(save_img_folder, '{}.jpg'.format(img_name)), img)
        np.savetxt(save_name, boxes_list.reshape(-1, 8), delimiter=',', fmt='%d')
    print('fps:{}'.format(total_frame / total_time))
    return save_txt_folder


if __name__ == '__main__':
    os.environ['CUDA_VISIBLE_DEVICES'] = str('1')
    backbone = 'resnet152'
    scale = 4
    args = parse_args()
    model_path = args.model_path
    data_path = args.data_path
    gt_path = args.gt_path
    save_path = args.save_path

    gpu_id = 0
    print('backbone:{},scale:{},model_path:{}'.format(backbone,scale,model_path))
    save_path = main(model_path, backbone, scale, data_path, save_path, gpu_id=gpu_id)
    result = cal_recall_precison_f1(gt_path=gt_path, result_path=save_path)
    print(result)
    # print(cal_recall_precison_f1('/data2/dataset/ICD151/test/gt', '/data1/zj/tensorflow_PSENet/tmp/'))
