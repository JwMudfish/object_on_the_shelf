import time
import cv2
import numpy as np
from skimage.measure import compare_ssim
import os
from glob import glob
from box_utils import BoxUtils
import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis
import json
from keys import keys

start_time = time.time()

RESIZE = 224
THRESHOLD = 0.88

image_dir = './test_images'
store_id = '00766'
device_id = 'w_00001'


##################################### DB 설정 ######################################
host = '125.132.250.228'
port = 6379
db = 2
username = 'worker'
password = keys.get('redis', './keys')

r2 = redis.Redis(host = host, port = port, db = db, username = username, password=password)

engine = create_engine(f'postgresql://postgres:{keys.get("postgres", "./keys")}@database-1.ctnphj2dxhnf.ap-northeast-2.rds.amazonaws.com:5432/emart24')
Session = sessionmaker(bind=engine)
session = Session()

#####################################################################################

'''
def connect_redis(host, port, db, username, password):
    r2 = redis.Redis(host = host, port = port, db = db, username = username, password=password)
    return r2
    
def get_images_from_redis(stord_id, device_type, device_id, r2):
    # r2 = connect_redis(host=host, port=port, db=db, username=username, password=password)
    full_image_list = []
    for i in range(0,5):    # 독립형 / 워크인 모드로 변수화 시켜야함
        img = r2.get(f'{store_id}_{device_type}_{device_id}_cam{i}')
        encoded_img = np.frombuffer(img, dtype = np.uint8)
        image = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        full_image_list.append(image)
    return full_image_list
'''

def get_design_label(pkey):
    result = session.query(models.Design).filter_by(design_pkey=pkey).first()
    return result.design_infer_label


def get_vision_result(r2):
    if device_id.split('_')[0] == 'w':
        floor = [0, 1, 2, 3, 4, 5]
        cell = range(8)

    elif device_id.split('_')[0] == 's':
        floor = [0, 1, 2, 3]  # 독립형 4단짜리, 5단짜리 나눠야 할수도 있음
        cell = range(7)

    result = []
    for f in floor:
        result.append([get_design_label(int(r2.get(f'{store_id}_{device_id}_f{f}_c{c}_inf_result'))) for c in cell])

    return result

def adjust_vision_result(vision_result):  # box 7개
    rst = []
    for vision_list in vision_result:
        vision_result = list(map(lambda x : x.split('_')[-1], vision_list))
        result = vision_result.copy()
        for i in range(len(vision_result)-3):         # 독립형 기준
            if vision_result[i] == 'pet':
                if i > 0:
                    result[i-1] = 'pet'
                result[i+1] = 'pet'
        rst.append(result)
    return rst


def adjust_vision_result_v2(vision_result):    # box 14개
    vision_result_p = vision_result
    vr_cp = vision_result_p.copy()

    rst = [[i,j] for i,j in zip(vr_cp, vision_result_p)]
    vision_result = np.array(rst).reshape(1,14).tolist()[0]

    result = vision_result.copy()
    for i in range(len(vision_result)-6):         # 독립형 기준
        if vision_result[i] == 'pet':
            if i > 0:
                result[i-1] = 'pet'
            result[i+1] = 'pet'
    return result

def read_image_gray(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.GaussianBlur(image, (0,0), 1.0)
    #image = cv2.resize(image, (RESIZE, RESIZE))
    return image

def is_object(p_image_path, f_image_path, threshhold):
    grayF = read_image_gray(f_image_path)
    grayP = read_image_gray(p_image_path)

    (score, diff) = compare_ssim(grayP, grayF, full=True, gaussian_weights=False)
    score = round(score, 3)
    diff = (diff * 255).astype('uint8')

    if score < THRESHOLD:
        return ('F', score)
    else:
        return ('T', score)

def get_pair_image(image_dir, store_id, device_id, floor):
    p_images = sorted(glob(os.path.join(image_dir, store_id, device_id, str(floor), 'p/*')))
    f_images = sorted(glob(os.path.join(image_dir, store_id, device_id, str(floor), 'f/*')))

    if len(p_images) != len(f_images):
        return 'f_images, f_images are not same'

    return p_images, f_images

def result_to_dict(final_tf, final_score, final_rst):
    rst = {}
    cnt = 0
    for x,y,z in zip(final_tf, final_score, final_rst):
        rst[str(cnt)] = {'tf' : x, 'score' : y, 'result' : z}
        cnt += 1
    return rst

def result_to_redis(store_id, device_id, r2, data):
    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    r2.set(f'{store_id}_{device_id}_is_object', data)



#vision_result = ['coca_200_can','sprite_300_can','pocari_300_can','demisoda_400_pet','cider_244_can','drpper_200_can','power_200_can']
vision_result = get_vision_result(r2)
#print(vision_result)
#print("")
vision_result = adjust_vision_result (vision_result)
#print(vision_result)
#print("")

final_tf = []
final_score = []
final_rst = []

for floor in range(6):  # 6단이라서 ---- 변수화 시켜야함
    p_images, f_images = get_pair_image(image_dir, store_id, device_id, floor)

    result = [is_object(p, f, threshhold = THRESHOLD)[0] for p, f in zip(p_images, f_images)]
    result_score = [is_object(p, f, threshhold = THRESHOLD)[1] for p, f in zip(p_images, f_images)]

    final_result = [v if v == 'pet' else o for v, o in zip(vision_result[floor], result)]

    if 'F' in final_result:
        #print('error')
        final_rst.append('error')
    else:
        #print('Fine')
        final_rst.append('fine')

    final_tf.append(final_result)
    final_score.append(result_score)
 
print(final_tf)
print(final_score)
print(final_rst)
#print(vision_result)

data = result_to_dict(final_tf, final_score, final_rst)
result_to_redis(store_id, device_id, r2, data)

from pprint import pprint
pprint(result_to_dict(final_tf, final_score, final_rst))

print('걸리는 시간 : ', time.time() - start_time)

