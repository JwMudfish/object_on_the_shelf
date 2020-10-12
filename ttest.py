#from class_test import box_crop
from class_test import box_crop

a = box_crop.get_boxes(xml_path = './boxes')
print(a)

b = box_crop.get_labels(label_path = './label.txt')
print(b)