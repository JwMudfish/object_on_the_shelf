import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd
import cv2
import numpy as np
from datetime import datetime
import os

class BoxUtils:

    """
    BoxUtils Class
    Author : JwMudfish
    Date : 2020.09.24
    """

    def get_boxes(xml_path):

        label_path = xml_path
        xml_list = os.listdir(label_path)

        boxes_1 = {}
        cnt = 0
        for xml_file in sorted(xml_list):
            if xml_file =='.DS_Store':
                pass
            else:
                    #try:
                xml_path = os.path.join(label_path,xml_file)

                root_1 = minidom.parse(xml_path)
                bnd_1 = root_1.getElementsByTagName('bndbox')

                result = []
                for i in range(len(bnd_1)):
                    xmin = int(bnd_1[i].childNodes[1].childNodes[0].nodeValue)
                    ymin = int(bnd_1[i].childNodes[3].childNodes[0].nodeValue)
                    xmax = int(bnd_1[i].childNodes[5].childNodes[0].nodeValue)
                    ymax = int(bnd_1[i].childNodes[7].childNodes[0].nodeValue)
                    result.append((xmin,ymin,xmax,ymax))

                boxes_1[str(cnt)] = result
                cnt += 1
        return boxes_1


    def get_labels(label_path):
        with open('./label.txt', 'r') as file:
            labels = file.readlines()
            labels = list(map(lambda x : x.strip(), labels))

        return labels

    def crop_image(image, boxes, save_path, labels, resize=None):
            seed_image = image
            images = list(map(lambda b : image[b[1]+1:b[3]-1, b[0]+2:b[2]-1], boxes))
            images = list(map(lambda i : cv2.resize(i, resize), images))

            num = 0            
            for img, label in zip(images, labels):
                num = num + 1
                cv2.imwrite('{}/{}/{}_{}_{}.jpg'.format(save_path,label,today,label, num), img)
                #cv2.imwrite('{}/{}/{}_{}.jpg'.format(save_path,label,today,label), img)
            return images
