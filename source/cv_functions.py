import numpy as np
import cv2
import dicom

def load_image(path=""):

    tmp_path = path.split(".")

    if(tmp_path[len(tmp_path)-1].upper() == "DCM"):
        dicom_data = dicom.read_file(fi)
        dicom_numpy = dicom_data.pixel_array

        dicom_normal = normalizing(binary_img=dicom_numpy)

        area1 = np.mean(dicom_normal[:int(dicom_numpy.shape[0]/4), :int(dicom_numpy.shape[1]/4)])
        area2 = np.mean(dicom_normal[int(dicom_numpy.shape[0]/4*3):, :int(dicom_numpy.shape[1]/4)])
        area3 = np.mean(dicom_normal[:int(dicom_numpy.shape[0]/4), int(dicom_numpy.shape[1]/4*3):])
        area4 = np.mean(dicom_normal[int(dicom_numpy.shape[0]/4*3):, int(dicom_numpy.shape[1]/4*3):])

        threshold = np.mean([area1, area2, area3, area4])
        if(threshold > 127):
            dicom_normal = 255 - dicom_normal

        return dicom_normal
    else:
        return cv2.imread(path)


def save_image(path="", filename="", image=None):

    # print("Save: "+str(path+filename))
    cv2.imwrite(path + filename, image)

def rgb2gray(rgb=None):

    return cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

def resizing(image=None, width=0, height=0):

    # set ratio
    if(width == 0):
        width = int(image.shape[1] / image.shape[0] * height)
    elif(height == 0):
        height = int(image.shape[0] / image.shape[1] * width)
    else:
        pass

    return cv2.resize(image, (width, height))

def bluring(binary_img=None, k_size=11):
    binary_img = binary_img.astype('uint8')

    return cv2.GaussianBlur(binary_img, (k_size, k_size), 0)

def normalizing(binary_img=None):

    sumx = np.sum(binary_img) / (binary_img.shape[0]*binary_img.shape[1])
    normal = (binary_img / sumx) * 127

    return normal

def adaptiveThresholding(binary_img=None, neighbor=5, blur=False, blur_size=3):
    binary_img = binary_img.astype('uint8')

    if(blur):
        binary_img = cv2.GaussianBlur(binary_img, (blur_size, blur_size), 0)
    return cv2.adaptiveThreshold(binary_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, neighbor, 1)

def erosion(binary_img=None, k_size=5, iterations=1):

    kernel = np.ones((k_size, k_size),np.uint8)

    return cv2.erode(binary_img, kernel, iterations=iterations)

def dilation(binary_img=None, k_size=5, iterations=1):

    kernel = np.ones((k_size, k_size),np.uint8)

    return cv2.dilate(binary_img, kernel, iterations=iterations)

def custom_opeing(binary_img=None, ero_size=5, dil_size=5, iterations=1):

    ero_kernel = np.ones((ero_size, ero_size),np.uint8)
    dil_kernel = np.ones((dil_size, dil_size),np.uint8)

    tmp_ero = cv2.erode(binary_img, ero_kernel, iterations=iterations)

    return cv2.dilate(tmp_ero, dil_kernel, iterations=iterations)

def custom_closing(binary_img=None, ero_size=5, dil_size=5, iterations=1):

    ero_kernel = np.ones((ero_size, ero_size),np.uint8)
    dil_kernel = np.ones((dil_size, dil_size),np.uint8)

    tmp_dil = cv2.dilate(binary_img, dil_kernel, iterations=iterations)

    return cv2.erode(tmp_dil, ero_kernel, iterations=iterations)

def opening(binary_img=None, k_size=2, iterations=1):

    kernel = np.ones((k_size, k_size), np.uint8)

    return cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel, iterations=iterations) # iteration = loop

def closing(binary_img=None, k_size=2, iterations=1):

    kernel = np.ones((k_size, k_size), np.uint8)

    return cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel, iterations=iterations) # iteration = loop

def contouring(binary_img=None):
    binary_img = binary_img.astype('uint8')

    # return two values: contours, hierarchy
    # cv2.RETR_EXTERNAL
    img, contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def contour2box(contours=None, padding=10):

    boxes =[]
    for cnt in contours:

        area = cv2.contourArea(cnt)
        # if(area < 30):
        #     continue

        x, y, w, h = cv2.boundingRect(cnt)
        x, y, w, h = x-int(padding/2), y-int(padding/2), w+int(padding), h+int(padding)
        boxes.append([x, y, w, h])

    return boxes

def rid_repetition(boxes=None, binary_img=None):

    box_rid = []
    for i in range(len(boxes)): # rid repetition area
        x_i, y_i, w_i, h_i = boxes[i]

        cnt = 0
        for j in range(len(boxes)):
            x_j, y_j, w_j, h_j = boxes[j]

            if(i == j):
                continue
            else:
                if((x_j > 0) and (y_j > 0)):
                    if((x_j+w_j < binary_img.shape[1]) and (y_j+h_j < binary_img.shape[0])):
                        if((x_i >= x_j) and (y_i >= y_j) and (x_i+w_i <= x_j+w_j) and (y_i+h_i <= y_j+h_j)): # box_i is in box_j
                            cnt += 1

        if(cnt == 0):
            if((x_i > 0) and (y_i > 0)):
                if((x_i+w_i < binary_img.shape[1]) and (y_i+h_i < binary_img.shape[0])):
                    box_rid.append([x_i, y_i, w_i, h_i])

    return box_rid

def density_filter(binary_img=None, k_size=3, dense=0.5):

    clone = binary_img
    for y in range(binary_img.shape[0]):
        if(y+k_size > binary_img.shape[0]):
            break
        for x in range(binary_img.shape[1]):
            if(x+k_size > binary_img.shape[1]):
                break
            else:
                cnt = np.count_nonzero(binary_img[y:y+k_size, x:x+k_size])
                if(cnt > k_size**2*dense):
                    clone[y+int(k_size/2), x+int(k_size/2)] = 255
                else:
                    clone[y+int(k_size/2), x+int(k_size/2)] = 0

    return clone

def moving_avg_filter(binary_img=None, k_size=3):

    binary_img = zero_padding(image=binary_img, height=binary_img.shape[0]+(k_size*2), width=binary_img.shape[1]+(k_size*2))

    clone = binary_img
    for y in range(binary_img.shape[0]):
        if(y+k_size > binary_img.shape[0]):
            break
        for x in range(binary_img.shape[1]):
            if(x+k_size > binary_img.shape[1]):
                break
            else:
                avg = np.average(binary_img[y:y+k_size, x:x+k_size])
                clone[y+int(k_size/2), x+int(k_size/2)] = avg

    crop_pad = clone[k_size:clone.shape[0]-k_size, k_size:clone.shape[1]-k_size]
    crop_pad = crop_pad.astype('uint8')
    return crop_pad

def feeding_outside_filter(binary_img=None, thresh=127):

    clone = binary_img

    for x in range(binary_img.shape[1]):
        limit = 0
        for y in range(binary_img.shape[0]):
            if(binary_img[y, x] > thresh):
                limit = y
                break
        clone[:limit, x] = np.ones((limit)) * 255

    for y in range(binary_img.shape[0]):
        limit = 0
        for x in range(binary_img.shape[1]):
            if(binary_img[y, x] > thresh):
                limit = x
                break
        clone[y, :limit] = np.ones((limit)) * 255

    for y in range(binary_img.shape[0]):
        limit = 0
        for x in range(binary_img.shape[1]):
            if(binary_img[y, binary_img.shape[1]-1-x] > thresh):
                limit = x
                break
        clone[y, binary_img.shape[1]-limit:] = np.ones((limit)) * 255

    return clone

def zero_padding(image=None, height=100, width=100, channel=1):

    pad = np.zeros((height, width, channel))
    if(channel == 1):
        pad = np.zeros((height, width))

    mid_y = int(pad.shape[0]/2) # mid of y
    mid_x = int(pad.shape[1]/2) # mid of x
    half_h = int(image.shape[0]/2) # height/2 of image
    half_w = int(image.shape[1]/2) # width/2 of image

    s_py = mid_y-half_h
    s_px = mid_x-half_w
    e_py = mid_y-half_h+image.shape[0]
    e_px = mid_x-half_w+image.shape[1]

    if((image.shape[1] < min(pad.shape)) and (image.shape[0] < min(pad.shape))):
        pad[s_py:e_py, s_px:e_px] = pad[s_py:e_py, s_px:e_px] + image
    else:
        x_limit = min(pad.shape[1], image.shape[1])
        y_limit = min(pad.shape[0], image.shape[0])

        crop = image[:y_limit, :x_limit]
        half_h = int(crop.shape[0]/2) # height/2 of image
        half_w = int(crop.shape[1]/2) # width/2 of image

        s_py = mid_y-half_h
        s_px = mid_x-half_w
        e_py = mid_y-half_h+crop.shape[0]
        e_px = mid_x-half_w+crop.shape[1]
        pad[s_py:e_py, s_px:e_px] = pad[s_py:e_py, s_px:e_px] + crop

    return pad

def remain_only_center(binary_img=None):


    contours = contouring(binary_img=binary_img)
    boxes = contour2box(contours=contours, padding=0)

    box_rid = rid_repetition(boxes=boxes, binary_img=binary_img)

    boxes_new = []
    for box in box_rid:
        x, y, w, h = box

        if((x > 0) and (y > 0)):
            if((x+w < binary_img.shape[1]) and (y+h < binary_img.shape[0])):

                box_x = (x + (x + w)) / 2
                box_y = (y + (y + h)) / 2

                img_x = binary_img.shape[1] / 2
                img_y = binary_img.shape[0] / 2

                dist = np.sqrt((box_x - img_x)**2 + (box_y - img_y)**2)
                boxes_new.append([x, y, w, h, dist])

    boxes_new = sorted(boxes_new, key=lambda l:l[4], reverse=False) # sort by short distance

    for idx in range(len(boxes_new)):
        if(idx == 0):
            continue
        x, y, w, h, dist = boxes_new[idx]

        if((x > 0) and (y > 0)):
            if((x+w < binary_img.shape[1]) and (y+h < binary_img.shape[0])):
                binary_img[y:y+h, x:x+w] = 0

    binary_img = dilation(binary_img=binary_img, k_size=2, iterations=10)
    binary_inv = 255 - binary_img

    contours = contouring(binary_img=binary_inv)
    boxes = contour2box(contours=contours, padding=0)

    boxes_new = []
    for box in boxes:
        x, y, w, h = box
        boxes_new.append([x, y, w, h, w*h])

    boxes_new = sorted(boxes_new, key=lambda l:l[4], reverse=True) # sort by bigger box

    for idx in range(len(boxes_new)):
        if(idx <= 1):
            continue
        x, y, w, h, dist = boxes_new[idx]

        if((x > 0) and (y > 0)):
            if((x+w < binary_inv.shape[1]) and (y+h < binary_inv.shape[0])):
                binary_inv[y:y+h, x:x+w] = 0

    binary_rev = 255 - binary_inv

    contours = contouring(binary_img=binary_rev)
    boxes = contour2box(contours=contours, padding=0)

    boxes_new = []
    for box in boxes:
        x, y, w, h = box

        if((x > 0) and (y > 0)):
            if((x+w < binary_rev.shape[1]) and (y+h < binary_rev.shape[0])):

                box_x = (x + (x + w)) / 2
                box_y = (y + (y + h)) / 2

                img_x = binary_rev.shape[1] / 2
                img_y = binary_rev.shape[0] / 2

                dist = np.sqrt((box_x - img_x)**2 + (box_y - img_y)**2)
                boxes_new.append([x, y, w, h, dist])

    boxes_new = sorted(boxes_new, key=lambda l:l[4], reverse=False) # sort by short distance

    for idx in range(len(boxes_new)):
        if(idx == 0):
            continue
        x, y, w, h, dist = boxes_new[idx]

        if((x > 0) and (y > 0)):
            if((x+w < binary_rev.shape[1]) and (y+h < binary_rev.shape[0])):
                binary_rev[y:y+h, x:x+w] = 0

    return binary_rev

def remain_only_biggest(binary_img=None):


    contours = contouring(binary_img=binary_img)
    boxes = contour2box(contours=contours, padding=0)

    box_rid = rid_repetition(boxes=boxes, binary_img=binary_img)

    boxes_new = []
    for box in box_rid:
        x, y, w, h = box

        if((x > 0) and (y > 0)):
            if((x+w < binary_img.shape[1]) and (y+h < binary_img.shape[0])):
                size = w * h
                boxes_new.append([x, y, w, h, size])

    boxes_new = sorted(boxes_new, key=lambda l:l[4], reverse=True) # sort by biggest order

    for idx in range(len(boxes_new)):
        if(idx == 0):
            continue
        x, y, w, h, size = boxes_new[idx]

        if((x > 0) and (y > 0)):
            if((x+w < binary_img.shape[1]) and (y+h < binary_img.shape[0])):
                binary_img[y:y+h, x:x+w] = 0

    binary_img = dilation(binary_img=binary_img, k_size=2, iterations=10)
    binary_inv = 255 - binary_img

    contours = contouring(binary_img=binary_inv)
    boxes = contour2box(contours=contours, padding=0)

    boxes_new = []
    for box in boxes:
        x, y, w, h = box
        boxes_new.append([x, y, w, h, w*h])

    boxes_new = sorted(boxes_new, key=lambda l:l[4], reverse=True) # sort by bigger box

    for idx in range(len(boxes_new)):
        if(idx <= 1):
            continue
        x, y, w, h, size = boxes_new[idx]

        if((x > 0) and (y > 0)):
            if((x+w < binary_inv.shape[1]) and (y+h < binary_inv.shape[0])):
                binary_inv[y:y+h, x:x+w] = 0

    binary_rev = 255 - binary_inv

    contours = contouring(binary_img=binary_rev)
    boxes = contour2box(contours=contours, padding=0)

    boxes_new = []
    for box in boxes:
        x, y, w, h = box

        if((x > 0) and (y > 0)):
            if((x+w < binary_rev.shape[1]) and (y+h < binary_rev.shape[0])):
                size = w * h
                boxes_new.append([x, y, w, h, size])

    boxes_new = sorted(boxes_new, key=lambda l:l[4], reverse=True) # sort by bigger box

    for idx in range(len(boxes_new)):
        if(idx == 0):
            continue
        x, y, w, h, size = boxes_new[idx]

        if((x > 0) and (y > 0)):
            if((x+w < binary_rev.shape[1]) and (y+h < binary_rev.shape[0])):
                binary_rev[y:y+h, x:x+w] = 0

    return binary_rev
