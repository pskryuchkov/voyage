# This code is rework of places365: https://github.com/CSAILVision/places365
# Depency: http://places2.csail.mit.edu/models_places365/W_sceneattribute_wideresnet18.npy
# Version: 0.4


from os.path import isdir, isfile, join
from os import listdir
import argparse
import json
import sys

import numpy as np
from scipy.misc import imresize as imresize
from PIL import Image
import cv2

import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F

import wideresnet


def init_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--city", required=True, help="name of the city")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return vars(parser.parse_args())


def load_labels():
    file_name_category = 'categories_places365.txt'

    classes = list()
    with open(file_name_category) as class_file:
        for line in class_file:
            classes.append(line.strip().split(' ')[0][3:])
    classes = tuple(classes)

    # indoor and outdoor relevant
    file_name_IO = 'IO_places365.txt'

    with open(file_name_IO) as f:
        lines = f.readlines()
        labels_IO = []
        for line in lines:
            items = line.rstrip().split()
            labels_IO.append(int(items[-1]) -1) # 0 is indoor, 1 is outdoor
    labels_IO = np.array(labels_IO)

    # scene attribute relevant
    file_name_attribute = 'labels_sunattribute.txt'

    with open(file_name_attribute) as f:
        lines = f.readlines()
        labels_attribute = [item.rstrip() for item in lines]
    file_name_W = 'W_sceneattribute_wideresnet18.npy'

    W_attribute = np.load(file_name_W)

    return classes, labels_IO, labels_attribute, W_attribute

def hook_feature(module, input, output):
    features_blobs.append(np.squeeze(output.data.cpu().numpy()))


def returnTF():
    tf = trn.Compose([
        trn.Resize((224,224)),
        trn.ToTensor(),
        trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return tf


def load_model():
    model_file = 'wideresnet18_places365.pth.tar'

    model = wideresnet.resnet18(num_classes=365)
    checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
    state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)
    model.eval()

    model.eval()
    features_names = ['layer4','avgpool']
    for name in features_names:
        model._modules.get(name).register_forward_hook(hook_feature)
    return model


args = init_arguments()
city = args['city']

path = "../../photos/{}".format(city)
scenes_dir = "../../data/scenes"
scenes_path = join(scenes_dir, 'scenes_{}.json'.format(city))

scene_base = {}
if isfile(scenes_path):
    with open(scenes_path, 'r') as f:
        scene_base = json.load(f)

classes, labels_IO, labels_attribute, W_attribute = load_labels()

features_blobs = []
model = load_model()

tf = returnTF() 

params = list(model.parameters())
weight_softmax = params[-2].data.numpy()
weight_softmax[weight_softmax < 0] = 0

areas = [f for f in listdir(path) if isdir(join(path, f))]

saving_interval = 10
json_indent = 4

global_locations_cn = 0
for area in areas:
    locations = listdir(join(path, area))
    for k, loc in enumerate(locations):
        global_locations_cn += 1

        if loc in scene_base:
            print("Processed:", loc)
            continue

        print(global_locations_cn, loc)
        
        pictures = []
        if isdir(join(path, area, loc)):
            pictures = listdir(join(path, area, loc))

        scene_base[loc] = {}

        for pic in pictures:
            try:
                img = Image.open(join(path, area, loc, pic))
            except:
                continue

            input_img = V(tf(img).unsqueeze(0))

            try:
                logit = model.forward(input_img)
            except Exception as e:
                print(e)

            h_x = F.softmax(logit, 1).data.squeeze()
            probs, idx = h_x.sort(0, True)
            probs = probs.numpy()
            idx = idx.numpy()

            scene_proporties = {}
            io_image = np.mean(labels_IO[idx[:10]])
            if io_image < 0.5:
                scene_proporties['enviroment'] = 'indoor'
            else:
                scene_proporties['enviroment'] = 'outdoor'

            scene_proporties['categories'] = {}
            for i in range(0, 5):
                scene_proporties['categories'][classes[idx[i]]] = str(probs[i])

            responses_attribute = W_attribute.dot(features_blobs[1])
            idx_a = np.argsort(responses_attribute)
            scene_proporties['attributes'] = [labels_attribute[idx_a[i]] for i in range(-1,-10,-1)]

            scene_base[loc][pic] = scene_proporties
        
        if k % saving_interval == 0:
            with open(scenes_path, 'w') as fp:
                json.dump(scene_base, fp, indent=json_indent)