#import cv2
#import numpy as np

import time
import cv2
import numpy as np
from skimage.measure import compare_ssim
from PIL import Image, ImageFont, ImageDraw

start_time = time.time()
RESIZE = 224

def read_image_gray(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.GaussianBlur(image, (0,0), 1.0)
    #image = cv2.resize(image, (RESIZE, RESIZE))

    return image


p_image_path = './p_image/p_image_1.jpg'
f_image_path = './f_image/f_image_5.jpg'

p_image = cv2.imread(p_image_path)
f_image = cv2.imread(f_image_path)

grayF = read_image_gray(f_image_path)
grayP = read_image_gray(p_image_path)
#cv2.namedWindow('p_image', cv2.WINDOW_NORMAL)
#cv2.resizeWindow('p_image', 500,500)


# grayF = cv2.cvtColor(f_image, cv2.COLOR_BGR2GRAY)
# grayF = cv2.GaussianBlur(grayF, (0,0), 1.0)

# grayP = cv2.cvtColor(p_image, cv2.COLOR_BGR2GRAY)
# grayP = cv2.GaussianBlur(grayP, (0,0), 1.0)

#grayF = cv2.resize(grayF, (224,224))
#grayP = cv2.resize(grayP, (224,224))


(score, diff) = compare_ssim(grayP, grayF, full=True, gaussian_weights=False)
diff = (diff * 255).astype('uint8')
cv2.imshow('DIFF', diff)
text = 'SCORE: {:0.2f}'.format(score)
print('SSIM: {}'.format(score))

# ### PIL 이요ㅕㅇ해서 캠 옆에 ssim score 보여주기
font = ImageFont.truetype('NotoMono-Regular.ttf')
text_w, text_h = font.getsize(text)
w = 224
h = 224
#X_POS = w - text_w - 10
#Y_POS = h - text_h - 10

X_POS =  5
Y_POS =  5

pil_image = Image.fromarray(f_image)

draw = ImageDraw.Draw(pil_image)
draw.text((X_POS,Y_POS), text, (0,0,255), font=font)
f_image = np.array(pil_image)

if score < 0.90:
    cv2.rectangle(f_image, (0,0), (w,h), (0,0,255), 6)   # 6은 두께
    #print('There is Object on 1~3 column')
    print('경보발령 경보발령 !!!@@~~! 1~3 컬럼에 무엇인가가 있다!!!! 확인해봐 !!!!!!!!!!')
    
    cv2.namedWindow('Before Opened', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Before Opened', 500,500)
    cv2.namedWindow('After Closed', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('After Closed', 500,500)
    
    cv2.imshow('Before Opened', p_image)
    cv2.imshow('After Closed', f_image)

else:
    print('Fine')

print('걸리는 시간 : ', time.time() - start_time)

cv2.imshow('p_image', grayP)
cv2.imshow('f_image', grayF)


cv2.waitKey(0)
cv2.destroyAllWindows()

print(time.time() - start_time)
