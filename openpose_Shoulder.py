import cv2
import time
import numpy as np
import matplotlib.pyplot as plt #데이터 시각화 위하여 선언

#TODO:라이선스 확인 필요!!!!!!!!!!!!!!!!!!
"""
 *Original Code
 *https://github.com/spmallick/learnopencv
"""

MODE = "COCO"

if MODE is "COCO":
    protoFile = "pose/coco/pose_deploy_linevec.prototxt"
    weightsFile = "pose/coco/pose_iter_440000.caffemodel"
    nPoints = 18
    POSE_PAIRS = [[1, 0], [1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [1, 8], [8, 9], [9, 10], [1, 11], [11, 12],
                  [12, 13], [0, 14], [0, 15], [14, 16], [15, 17]]

elif MODE is "MPI":
    protoFile = "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
    weightsFile = "pose/mpi/pose_iter_160000.caffemodel"
    nPoints = 15
    POSE_PAIRS = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 5], [5, 6], [6, 7], [1, 14], [14, 8], [8, 9], [9, 10], [14, 11],
                  [11, 12], [12, 13]]

inWidth = 368
inHeight = 368
threshold = 0.1

#input_source = "sample_video.mp4"
#TODO:실시간 위해 수정
cap = cv2.VideoCapture(0)
hasFrame, frame = cap.read()

vid_writer = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                             (frame.shape[1], frame.shape[0]))

net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

#TODO:어깨 기울임 측정 값 저장 위해 list 추가 선언
Shoulder_result = [] #어깨 기울임 list 선언

while cv2.waitKey(1) < 0:
    t = time.time()
    hasFrame, frame = cap.read()
    frameCopy = np.copy(frame)
    if not hasFrame:
        cv2.waitKey()
        break

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                                    (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    output = net.forward()

    H = output.shape[2]
    W = output.shape[3]
    # Empty list to store the detected keypoints
    points = []

    for i in range(nPoints):
        # confidence map of corresponding body's part.
        probMap = output[0, i, :, :]

        # Find global maxima of the probMap.
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

        # Scale the point to fit on the original image
        x = (frameWidth * point[0]) / W
        y = (frameHeight * point[1]) / H

        if prob > threshold:
            cv2.circle(frameCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        lineType=cv2.LINE_AA)

            # Add the point to the list if the probability is greater than the threshold
            points.append((int(x), int(y)))
        else:
            points.append(None)

    # TODO:어깨 기울임 측정 위해 어깨만 색 다르게 추출하기 위하여 코드 변경
    #      및 어깨 기울임 측정위해  부가적인 코드 변경 [86~108][123~124]

    temp_a=0 #Right shoulder
    temp_b=0 #left shoulder
    temp=0
    temp2=0

    # Draw Skeleton
    for pair in POSE_PAIRS:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            if (partA==1 and partB==2) or (partA==1 and partB==5): #Neck-Right Shoulder, Neck-left Shoulder일 경우
                cv2.line(frame, points[partA], points[partB], (255, 0, 0), 3, lineType=cv2.LINE_AA) #다른 색으로 표시
                cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.circle(frame, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                if partB==2: #Right Shoulder인 경우 좌표 저장
                    temp_a=points[partB]
                if partB==5: #left Shoulder인 경우 좌표 저장
                    temp_b=points[partB]
                    temp=temp_a[0]-temp_b[0] #기울기 구하기 위하여 x증가량
                    temp2=temp_a[1]-temp_b[1] #기울기 구하기 위하여 y증가량
                    Shoulder_result.append(abs(temp2)/abs(temp)) #절대값을 이용하여 기울기를 구한 후 list에 저장

            else:
                cv2.line(frame, points[partA], points[partB], (0, 255, 255), 3, lineType=cv2.LINE_AA)
                cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.circle(frame, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

    cv2.putText(frame, "time taken = {:.2f} sec".format(time.time() - t), (50, 50), cv2.FONT_HERSHEY_COMPLEX, .8,
                (255, 50, 0), 2, lineType=cv2.LINE_AA)
    # cv2.putText(frame, "OpenPose using OpenCV", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 50, 0), 2, lineType=cv2.LINE_AA)
    # cv2.imshow('Output-Keypoints', frameCopy)
    cv2.imshow('Output-Skeleton', frame)

    vid_writer.write(frame)

plt.plot(Shoulder_result) #실시간 어깨 측정 종료시 그래프로 시각화
plt.show() #그래프 표시
vid_writer.release()

