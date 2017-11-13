import os, inspect
import cv2

import numpy as np

import source.cv_functions as cvf
import source.utility as util

PACK_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def tmp_main():

    img = cvf.load_image(path="/home/visionlab/Desktop/images/lung_image/POST/IMG-0012-00001.bmp")
    print(img.shape)

    gray = cvf.rgb2gray(rgb=img)
    print(gray.shape)

    res = cvf.resizing(image=gray, width = 500)
    print(res.shape)
    print("AVG: "+str(np.average(res)))

    cvf.save_image(path=PACK_PATH+"/images/", filename="origin.png", image=img)
    cvf.save_image(path=PACK_PATH+"/images/", filename="resize.png", image=res)

    ret,thresh1 = cv2.threshold(res, 127, 255, cv2.THRESH_BINARY)
    ret,thresh2 = cv2.threshold(res, np.average(res), 255, cv2.THRESH_BINARY_INV)
    ret,thresh3 = cv2.threshold(res, 127, 255, cv2.THRESH_TRUNC)
    ret,thresh4 = cv2.threshold(res, 127, 255, cv2.THRESH_TOZERO)
    ret,thresh5 = cv2.threshold(res, 127, 255, cv2.THRESH_TOZERO_INV)

    cvf.save_image(path=PACK_PATH+"/images/", filename="inverse_thresh.png", image=thresh2)

    erosed = cvf.erosion(binary_img=thresh2, k_size=5, iterations=1)
    cvf.save_image(path=PACK_PATH+"/images/", filename="erosion.png", image=erosed)

    dilated = cvf.dilation(binary_img=erosed, k_size=10, iterations=1)
    cvf.save_image(path=PACK_PATH+"/images/", filename="opening_dilated.png", image=dilated)
    im2, contours, hierarchy = cvf.contouring(binary_img=dilated)

    boxes = cvf.contour2box(contours=contours, padding=15)

    cnt = 0
    for b in boxes:
        x, y, w, h = b

        if((x > 0) and (y > 0)):
            if((x < res.shape[1]) and (y < res.shape[0])):
                cvf.save_image(path=PACK_PATH+"/images/", filename="box_"+str(cnt)+".png", image=res[y:y+h, x:x+w])
                cnt += 1

    for b in boxes:
        x, y, w, h = b

        if((x > 0) and (y > 0)):
            if((x < res.shape[1]) and (y < res.shape[0])):
                cv2.rectangle(res,(x,y),(x+w,y+h),(255, 255, 255),2)


    cvf.save_image(path=PACK_PATH+"/images/", filename="withbox.png", image=res)

    cv2.imshow('image',res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def extract_segments(filename):

    tmp_sub, tmp_file = util.get_dir_and_file_name(path=filename)

    origin = cvf.load_image(path=filename)
    gray = cvf.rgb2gray(rgb=origin)
    resized = cvf.resizing(image=gray, width = 500)
    avg = np.average(resized)


    ret,thresh = cv2.threshold(resized, 127, 255, cv2.THRESH_BINARY_INV)

    erosed = cvf.erosion(binary_img=thresh, k_size=3, iterations=7)
    # dilated = cvf.dilation(binary_img=erosed, k_size=3, iterations=3)

    _, contours, _ = cvf.contouring(binary_img=erosed)
    boxes = cvf.contour2box(contours=contours, padding=50)

    cnt = 0
    for b in boxes:
        x, y, w, h = b

        if((x > 0) and (y > 0)):
            if((x < resized.shape[1]) and (y < resized.shape[0])):
                if(not(util.check_path(path=PACK_PATH+"/images/"+str(tmp_file)))):
                    util.make_path(path=PACK_PATH+"/images/"+str(tmp_file))

                cvf.save_image(path=PACK_PATH+"/images/"+str(tmp_file)+"/", filename=str(tmp_file)+"_"+str(cnt)+".png", image=resized[y:y+h, x:x+w])
                cnt += 1

    cvf.save_image(path=PACK_PATH+"/images/"+str(tmp_file)+"/", filename="origin.png", image=origin)
    cvf.save_image(path=PACK_PATH+"/images/"+str(tmp_file)+"/", filename="thresh.png", image=thresh)
    cvf.save_image(path=PACK_PATH+"/images/"+str(tmp_file)+"/", filename="erosed.png", image=erosed)

    for b in boxes:
        x, y, w, h = b

        if((x > 0) and (y > 0)):
            if((x < resized.shape[1]) and (y < resized.shape[0])):
                cv2.rectangle(resized,(x,y),(x+w,y+h),(255, 255, 255),2)
                cv2.rectangle(erosed,(x,y),(x+w,y+h),(255, 255, 255),2)

    # cvf.save_image(path=PACK_PATH+"/images/"+str(tmp_file)+"/", filename="opened.png", image=dilated)
    cvf.save_image(path=PACK_PATH+"/images/"+str(tmp_file)+"/", filename="contour.png", image=erosed)
    cvf.save_image(path=PACK_PATH+"/images/"+str(tmp_file)+"/", filename="resized.png", image=resized)

def main():

    extensions = ["BMP", "bmp", "PNG", "png", "JPG", "jpg", "JPEG", "jpeg"]

    util.refresh_directory(PACK_PATH+"/images")

    print("Enter the path")
    usr_path = input(">> ")

    if(util.check_path(usr_path)):
        list_dir = util.get_dirlist(path=usr_path, save=False)
        print(list_dir)

        for li_d in list_dir:
            list_file = util.get_filelist(directory=usr_path+"/"+li_d, extensions=extensions)

            for li_f in list_file:
                print(li_f)
                extract_segments(filename=li_f)

    else:
        print("Invalid path :"+usr_path)

if __name__ == '__main__':

    # tmp_main()
    main()