# This is a sample Python script.
import cv2
import numpy as np



if __name__ == '__main__':
    INPUT_FILE1 = 'dancegirl.mp4'
    OUTPUT_FILE = 'merge.mp4'

    reader1 = cv2.VideoCapture(INPUT_FILE1,0)
    fps = reader1.get(cv2.CAP_PROP_FPS)
    width = int(reader1.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(reader1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(OUTPUT_FILE,
                             cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),  # (*"mp4v") for mp4 output
                             fps,  # fps
                             (width*2, height))  # resolution

    # print(reader1.isOpened())
    # print(reader2.isOpened())
    success = True
    c = 0
    success, frame1 = reader1.read()
    while success:
        print(type(frame1))
        img = np.hstack((frame1, frame1))
        print(img.shape)
        print(type(img))
        writer.write(img)
        c += 1
        print(str(c) + ' is ok')
        success, frame1 = reader1.read()
        # break

    writer.release()
    reader1.release()
    cv2.destroyAllWindows()

