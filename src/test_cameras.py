
# import cv2

# for index in range(10):
#     cap = cv2.VideoCapture(index)

#     if cap.isOpened():
#         print(f"Camera Found at Index {index}")
#         cap.release()

import cv2

for idx in [0, 1]:

    print(f"\nTesting Camera {idx}")

    cap = cv2.VideoCapture(idx)

    print("Opened:", cap.isOpened())

    if cap.isOpened():

        ret, frame = cap.read()

        print("Read Frame:", ret)

        if ret:
            print("Resolution:", frame.shape)

    cap.release()