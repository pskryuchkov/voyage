# v0.3

import os
import cv2
import numpy as np
from wide_resnet import WideResNet
from os import listdir
from os.path import join
import numpy as np
from time import time
import json
from operator import itemgetter 
from pprint import pprint
import dlib

pretrained_model = "/Users/pavel/Sources/python/concepts/insta/cv_sandbox/weights.18-4.06.hdf5"
face_cascade = cv2.CascadeClassifier('../haarcascade_frontalface_default.xml')


def crop_face(img, img_size):
    try:
        input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except:
        return np.empty((0, 0))

    margin=0.4
    img_h, img_w, _ = np.shape(input_img)

    detector = dlib.get_frontal_face_detector()
    detected = detector(input_img, 1)
    faces = np.empty((len(detected), img_size, img_size, 3))

    if len(detected) > 0:
        for i, d in enumerate(detected):
            x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
            xw1 = max(int(x1 - margin * w), 0)
            yw1 = max(int(y1 - margin * h), 0)
            xw2 = min(int(x2 + margin * w), img_w - 1)
            yw2 = min(int(y2 + margin * h), img_h - 1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            # cv2.rectangle(img, (xw1, yw1), (xw2, yw2), (255, 0, 0), 2)
            faces[i, :, :, :] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))
    return faces


def main():
    img_size = 64
    margin = 0.4
    depth = 16
    k = 8

    weight_file = pretrained_model
    
    model = WideResNet(img_size, depth=depth, k=k)()
    model.load_weights(weight_file)

    #top_file = open("/Users/pavel/Desktop/insta/tables/top.csv", "r").readlines()[1:]

    #locations = [x.strip().split(",") for x in top_file]
    #yet_processed = [x.strip().split(",")[0] for x in open("genders_ages.csv", "r").readlines()]
    #locations = [
    #                ["poselok-tekstilshchiki-russia", "941915295933998"],
    #                ["zyuzino-russia", "1189095101199408"],
    #                ["golyanovo-russia", "13901832"]
    #            ]

    path = "/Users/pavel/Sources/python/concepts/insta/photos_moscow"

    loc_file = list(map(lambda x: x.strip().split(","), open(join(path, "loc_info.csv"), "r").readlines()[1:]))
    locations = [[x[2], x[0]] for x in loc_file]

    try:
        yet_processed = json.load(open('gender_ages_moscow.json', 'r'))
    except:
        yet_processed = {}

    ddata = yet_processed
    for j, loc in enumerate(locations):
        area, id = loc
        predicted_genders, predicted_ages = {}, {}

        if id in ddata:
            continue

        print(j+1, area, id)

        start = time()
        for w, x in enumerate(listdir(join(path, area, id))):
            #cropped_faces = crop_face(cv2.imread(join(path, loc[0], loc[1], x)))
            #if cropped_faces is not None:
            #    faces = np.array([cv2.resize(x, (img_size, img_size)) for x in cropped_faces])
            #else:
            #    continue
            faces = crop_face(cv2.imread(join(path, loc[0], loc[1], x)), img_size)

            if faces.size == 0:
                continue

            results = model.predict(faces)

            if results:
                #genders = [1 if x[1] > 0.5 else 0 for x in results[0]]
                #predicted_genders += zip([w]*len(genders), genders)
                genders = [float(x[0]) for x in results[0]]
                predicted_genders[x] = genders

                ages = list(results[1].dot(np.arange(0, 101).reshape(101, 1)).flatten())
                #predicted_ages += zip([w]*len(ages), ages)
                predicted_ages[x] = ages

        
        ddata[id] = {"area": area, "genders": predicted_genders, "ages": predicted_ages}

        if j % 10 == 0: 
            with open('gender_ages_moscow.json', 'w') as fp:
                json.dump(ddata, fp, indent=4)

        #with open("genders_ages.csv", "a") as f:
        #    f.write("{},{},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(id, area, np.mean(predicted_genders), np.std(predicted_genders), 
        #                                                    np.mean(predicted_ages), np.std(predicted_ages)))
        
        print(round(time() - start, 2))


if __name__ == '__main__':
    main()
