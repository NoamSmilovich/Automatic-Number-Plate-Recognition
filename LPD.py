import cv2
import numpy as np


def mask_plate(image_path):
    original = cv2.imread(image_path)
    resized = image_resize(original, width=2000)  # Image resize for optimal OCR results

    blur = cv2.GaussianBlur(resized, (7, 7), 0)  # Blurring after resize for smoother image
    frame_hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    low_h, low_s, low_v = 12, 0, 0
    high_h, high_s, high_v = 40, 255, 255
    frame_threshold = cv2.inRange(frame_hsv, (low_h, low_s, low_v), (high_h, high_s, high_v))  # Yellow mask
    blur = cv2.GaussianBlur(frame_threshold, (9, 9), 0)  # Mask blurring to reduce noise
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Thresholding

    number_of_white_pix = np.sum(frame_threshold == 255)  # Extracting only white pixels
    number_of_black_pix = np.sum(frame_threshold == 0)  # Extracting only black pixels

    if number_of_white_pix / (number_of_white_pix + number_of_black_pix) > 0.4:  # Checking if plate is yellow
        blur = cv2.GaussianBlur(th3, (9, 9), 0)
    else:  # B&W plate
        frame_bgr = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)
        blur = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((2, 2), np.uint8)
    eroded = cv2.erode(blur, kernel, iterations=2)  # Erosion to make digits bold
    masked = cv2.bitwise_and(resized, resized, mask=eroded)  # Masking plate image
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)  # Masked image to grayscale
    kernel = np.ones((2, 2), np.uint8)
    bfilter = cv2.bilateralFilter(gray, 77, 17, 17)  # Noise reduction

    # Additional image processing to make digits bold and reduce noise
    dilated = cv2.dilate(bfilter, kernel, iterations=3)
    blur = cv2.GaussianBlur(dilated, (3, 3), 0)
    smooth = cv2.addWeighted(blur, 1.5, dilated, -0.5, 0)
    blur = cv2.GaussianBlur(smooth, (9, 9), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    eroded = cv2.erode(th3, kernel, iterations=7)
    blur = cv2.GaussianBlur(eroded, (21, 21), 0)
    kernel = np.ones((7, 7), np.uint8)
    dilated = cv2.dilate(blur, kernel, iterations=3)

    # Saving masked image to file and returning its path
    cv2.imwrite("JPGs\\masked_plate.jpg", dilated)
    return "JPGs\\masked_plate.jpg"


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    if width is None:
        width = 800
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized