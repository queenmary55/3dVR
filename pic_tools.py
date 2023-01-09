# -*- coding: utf-8 -*-

'''
@Author  : cathyZhang
@File    : pic_tools.py
@Software: PyCharm
@Time    : 2022/3/14 10:35
'''
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import base64
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
# from PIL import Image
import numpy as np
import cv2
import logging
import os
import subprocess
import random
import time




def downloadPic(pic_url,local_file):
    pic_url = str(pic_url)
    if pic_url == '-1':
        return 0
    if '!' in pic_url:
        pic_url = pic_url.split('!')[0]
    try:
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        r = s.get(pic_url, stream=True, timeout=20)
        r.raw.decode_content = True
        if Path(local_file).exists():
            logging.info('local file is exist {}'.format(local_file))
            return 1
        if r.status_code == 200:
            with open(local_file, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return 1
        else:
            return 0
    except requests.exceptions.HTTPError as errh:
        logging.error("Http Error: {}".format(errh))
        return 0
    except requests.exceptions.ConnectionError as errc:
        logging.error("Error Connecting: {}".format(errc))
        return 0
    except requests.exceptions.Timeout as errt:
        logging.error("Timeout Error: {}".format(errt))
        return 0
    except requests.exceptions.RequestException as err:
        logging.error("OOps: Something Else  {}" .format(err))
        return 0

# def isValidImage(pathfile):
#     bValid = True
#     try:
#       Image.open(pathfile).verify()
#       # log.logger.info('the image is valid')
#     except:
#       bValid = False
#       logging.info('the image cant open')
#     return bValid

# def hbasePic(vid):
#     conn = happybase.Connection(host='10.42.128.38', port=9090, transport='buffered', protocol='binary')
#     ts = conn.table(b'pictures')
#     result = ts.row(row=str.encode(vid), columns=[b'data:pic'])
#     if not result:
#         logging.info('the vid have no pic in hbase')
#         return np.zeros(0)
#     pic_b = bytes.decode(result[b'data:pic'])
#     # print(pic_b)
#     imgdata = base64.b64decode(pic_b)
#     nparr = np.fromstring(imgdata, np.uint8)
#     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     return image

def cv2_letterbox_image(image, expected_size):
    try:
        ih, iw = image.shape[0:2]
        ew, eh = expected_size
        scale = min(eh / ih, ew / iw)
        nh = int(ih * scale)
        nw = int(iw * scale)
        image = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_CUBIC)
        top = (eh - nh) // 2
        bottom = eh - nh - top
        left = (ew - nw) // 2
        right = ew - nw - left
        new_img = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(128,128,128))
        logging.info(' cv2_letterbox_image  new_img {}'.format(type(new_img)))
        return new_img
    except Exception as e:
        return np.zeros(0)
        logging.error("cv2_letterbox_image exception: " + str(e))



def getFrame_video(path,filename):

    cap = cv2.VideoCapture(path)
    filename
    c = 1
    index = 0
    truc_name = filename.split('.')[0].replace('-','_').replace(' ', '').encode('utf-8').decode('utf-8')
    subdir = path.split(os.sep)[-1].split('/')[0].encode('utf-8').decode('utf-8')
    print(truc_name)
    # 格式化成2016-03-20 11:45:39形式
    daytime = time.strftime("%m%d", time.localtime())
    # frame_dir = '/ssd/feedid2tag/frame{}/{}/'.format(daytime,subdir)
    frame_dir = 'F:\\PycharmProjects\\clip_for_video\\video\\frame{}\\{}\\'.format(daytime,subdir)
    check_path(frame_dir)
    print("================="+frame_dir)



    frameRate = 100  # 帧数截取间隔（每隔100帧截取一帧）
    while (True):
        ret, frame = cap.read()
        if ret:
            if (c % frameRate == 0):
                print("开始截取视频第：" + str(c) + " 帧")
                # 这里就可以做一些操作了：显示截取的帧图片、保存截取帧到本地

                cv2.imwrite(frame_dir+truc_name+'_{:0>3d}.jpg'.format(index), frame)
                break
                index+=1
            c += 1
            cv2.waitKey(0)
        else:
            print("所有帧都已经保存完成")
            break
    cap.release()


def blurScore(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def RGB(img):
    r =np.mean(img[:, :, 0])
    g = np.mean(img[:, :, 1])
    b = np.mean(img[:, :, 2])
    if r>250 and g>250 and b>250:
        return True
    if r<10 and g<10 and b<10:
        return True
    return False

def randSave():
    rd = random.random()
    if rd>0.85:
        return True
    return False



def detectBlur(frame_dir):
    blur_threshold = 80.0
    print(frame_dir)
    for root, dirs, files in os.walk(frame_dir):
        if len(dirs)>0:
            for direct in dirs:
                sec_direct = root + '/' + direct
                for subroot,subdirs,subfiles in os.walk(sec_direct):
                    for subfile in subfiles:
                        imagePath = sec_direct+'/'+subfile
                        print(imagePath)
                        flag = randSave
                        # randSaveDir = '/root/feedid2tag/randSave'
                        blur1kDir = '/ssd/feedid2tag/blur1k'
                        # if flag:
                        #     subprocess.call('cp {}  {}'.format(filepath,randSaveDir),shell=True)
                        image = cv2.imread(imagePath)
                        rgbFlag = RGB(image)
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        fm = blurScore(gray)
                        print(fm)
                        if fm < blur_threshold or rgbFlag:
                            trashDir = blur1kDir+'/'+direct
                            check_path(trashDir)
                            subprocess.call('mv {}  {}'.format(imagePath, trashDir), shell=True)



def check_path(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)
        print('mkdir {}'.format(dirs))

def keyFrame(path):
    truc_url = path.split('/')[-1].split('.')[0]
    index = 0
    try:
        frame_dir = '/ssd/feedid2tag/frame/{}/'.format(truc_url)
        check_path(frame_dir)
        print("frame_dir is {}".format(frame_dir))
        print("the current directory is :" + os.getcwd())
        print(
            "the ffmpeg cmd is  :" + "ffmpeg -i {} -vf select='eq(pict_type\,I)' -vsync 2  -f image2 {}{}-%03d.jpeg".format(
                path,frame_dir, truc_url))

        subprocess.call(
            r"ffmpeg -i {} -vf select='eq(pict_type\,I)' -vsync 2  -f image2 {}{}-%03d.jpeg".format(
                path, frame_dir, truc_url
            ), shell=True,timeout=10)

    except Exception as e:
        logging.error("OOps: Something wrong  {}" .format(e))


if __name__ == "__main__":
    file_dir= r'F:\PycharmProjects\clip_for_video\mp4'
    # file_dir = '/ssd/feedid2tag/frame0324/zongyi'
    print(os.path.exists(file_dir))

    for root, dirs, files in os.walk(file_dir):
        # print("root", root)  # 当前目录路径
        # print("files", files)  # 当前路径下所有非目录子文件
        for file in files:
            filepath =  root+'/'+file
            print(filepath)
            # print(file)
            # keyFrame(filepath)
            getFrame_video(filepath,file)
            break

    # frame_dir = '/ssd/feedid2tag/frame'
    # detectBlur(frame_dir)
