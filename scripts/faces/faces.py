from os.path import join
from time import time
import multiprocessing
import cv2
import os
import json
import argparse
import sys
import numpy as np


def init_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--city", required=True, help="name of the city")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return vars(parser.parse_args())


def count_faces_cv(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return (len(faces))


def limitator(x):
    assert(isinstance(x, int))
    if x < 10:
        return x
    else:
        return 9


def main():
    SAVING_INTERVAL = 100

    args = init_arguments()
    CITY = args['city']

    PROJECT_DIR = "../.."
    JSON_PATH = join(PROJECT_DIR, 'data/faces', 'faces_{}.json'.format(CITY))
    PHOTOS_DIR = join(PROJECT_DIR, 'photos/{}'.format(CITY))
    IMG_EXTENSION = '.jpg'

    pool = multiprocessing.Pool()
    location_faces = {}

    if os.path.isfile(JSON_PATH):
        location_faces = json.load(open(JSON_PATH, 'r'))

    total = len(list(os.walk(PHOTOS_DIR)))
    counter = 0
    for root, dirs, files in os.walk(PHOTOS_DIR):
        photo_location = root.split("/")[-1]
        photo_paths = []
        for file in files:
            if file.endswith(IMG_EXTENSION):
                photo_paths.append(os.path.join(root, file))
        
        if photo_location in location_faces:
            print("Processed:", photo_location)
            counter += 1
            continue
            
        if photo_paths:
            print("{}/{} {}".format(counter+1, total, photo_location))

            start = time()
            images = []
            for w, x in enumerate(photo_paths):
                img = cv2.imread(x)
                if isinstance(img, np.ndarray):
                    images.append(img)
                else:
                    print("Error:", x)
            
            counters = pool.map(count_faces_cv, images)
            counters = list(map(limitator, counters))
            
            location_faces[photo_location] = "".join(map(str, counters))
            print("{:.2f} s".format(time() - start))

        if counter % SAVING_INTERVAL == 0:
            with open(JSON_PATH, 'w') as fp:
                json.dump(location_faces, fp, indent=4)

        counter += 1


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
main()