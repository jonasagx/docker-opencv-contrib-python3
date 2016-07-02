from bottle import route, run, template, request, redirect
import os
import cv2
import sys
import os.path
import tempfile
import base64

ocr = cv2.text.OCRTesseract_create()
original = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABUUlEQVQ4T43TP0iVURzG8c8VJEEQpIZ0CdRB1HAI3Ezc2qzBSREXkYiCcGiKahDxDyJIDSrh2qCbi+DsIA4uOuiiFBI4BBfuZsSRcy5v13vve9/tnN/vfM/vec7zFlT/evAHNzXq5e1ClYYZPEQH9rBfD1IJGMYzrMVDy1jHFdrxAd/i+q6lEjCNMxzhMYKUv/iN12jGCi7TVAnwBJ04xksMognneIQHWMB3TGUlJcAG3uINfuFHDd0DGMen7AT9mIi6TnCY4/wL9Caf0gQj+IzRnMPh5k28QiuWEqAPY1FnPcZHbOE6elVKgKd4jq95wcnUwxTFBAiOL0ZzSg1AgtnhZVazOejGJL7kAOaxHZ/4XpBCBoo4wFAMULjpJ8Jks7F2URmktJ6LSQwOd+EWLWiLEt/FjJzWAoT99zGquxkpIY0hyjsoH672LzTg3/8t/wCs6Tqb27/Z5AAAAABJRU5ErkJggg=='
result = original
list = []

def order(x,y):
	if x > y:
		return y, x
	else:
		return x, y

def tesseract(img, x, y, w, h):
	ret, mask = cv2.threshold(img, 255, 255, cv2.THRESH_BINARY) # make black mask
	print(x ,y ,w, h)
	x_min, x_max = order(x, w)
	for i in range(x_min, x_max):
		y_min, y_max = order(y, h)
		for j in range(y_min, y_max):
			mask[j][i] = 0
	ret = ocr.run(img, mask, 1)
	tmp_img = img[y:y+h, x:x+w]
	return ocr.run(tmp_img, 1)

def captch_ex(file):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(file.read())
        file_name = tf.name
    original  = cv2.imread(file_name)
    img2gray = cv2.cvtColor(original,cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 130, 255, cv2.THRESH_BINARY)
    img_final = cv2.bitwise_and(img2gray , img2gray , mask =  mask)
    ret, new_img = cv2.threshold(img_final, 80 , 255, cv2.THRESH_BINARY)  # for black text , cv.THRESH_BINARY_INV
    result = original.copy()
    '''
            line  8 to 12  : Remove noisy portion
    '''
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3 , 3)) # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
    dilated = cv2.dilate(new_img,kernel,iterations = 9) # dilate , more the iteration more the dilation

    i, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # get contours
    index = 0
    for contour in contours:
        # get rectangle bounding contour
        [x,y,w,h] = cv2.boundingRect(contour)

        #Don't plot small false positives that aren't text
        if w < 35 and h<35:
            print(w,h)
            continue

        # draw rectangle around contour on original image
        cv2.rectangle(result,(x,y),(x+w,y+h),(255,0,255),2)
        
        list.append(tesseract(img_final, x, y, w, h))

        #you can crop image and send to OCR  , false detected will return no text :)
        cropped = img_final[y :y +  h , x : x + w]
        s = file_name + '/crop_' + str(index) + '.jpg'
        cv2.imwrite(s , cropped)
        index = index + 1
    # write original image with added contours to disk
    #cv2.imshow('captcha_result' , img)
    #cv2.waitKey()
    cv2.imwrite('/usr/local/src/original.png', original)
    cv2.imwrite('/usr/local/src/result.png', result)
    cv2.imwrite('/usr/local/src/img2gray.png', img2gray)
    cv2.imwrite('/usr/local/src/mask.png', mask)
    cv2.imwrite('/usr/local/src/image_final.png', img_final)
    return original, result

@route('/')
def index():
    return template('form', original=original, result=result, list=list)


@route('/upload', method='POST')
def do_upload():
    global list
    list = []
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    original, result = captch_ex(upload.file)    
    with tempfile.NamedTemporaryFile() as tf:
        cv2.imwrite(tf.name + '_origin.png', original)
        cv2.imwrite(tf.name + '_result.png', result)
        with open(tf.name + '_origin.png', "rb") as imgfile:
            data = imgfile.read()
            global original
            original = 'data:image/png;base64,' + base64.encodestring(data).decode('utf8')
        with open(tf.name + '_result.png', "rb") as imgfile:
            data = imgfile.read()
            global result
            result = 'data:image/png;base64,' + base64.encodestring(data).decode('utf8')
    redirect('/')
run(host='0.0.0.0', port=8080)
