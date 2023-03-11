from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .bg import *

import os
import cv2
import numpy as np
import mediapipe as mp

from PIL import Image

# Create your views here.
#############Change the path before running##############

def index(request):
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

def pricing(request):
    return render(request,'pricing.html')

def background(request):
    BGRemover()
    return render(request, 'index.html')

def crop(request):
    return uploader(request, 'crop.html')
    
def change_color(request):
    return uploader(request, 'change_color.html')

def sharpen_image(request):
    return uploader(request, 'sharpen.html')

def uploader(request, html):
    global photo, photo0
    photo0 = "" 
    if request.method == 'POST' and request.FILES.get('image'):
        # Process the uploaded image
        uploaded_image = request.FILES['image']
        ext = os.path.splitext(uploaded_image.name)[1]
        if ext not in ['.png', '.jpg', '.jpeg', '.svg']:
            return render(request, html,{'error':"Invalid File Type"})
        fs = FileSystemStorage()
        filename = fs.save(uploaded_image.name, uploaded_image)
        photo = uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)
        if html=="image_bg.html":
            uploaded_image0 = request.FILES['image0']
            ext0 = os.path.splitext(uploaded_image0.name)[1]
            if ext0 not in ['.png', '.jpg', '.jpeg', '.svg']:
                return render(request, html,{'error':"Invalid File Type"})
            filename0 = fs.save(uploaded_image0.name, uploaded_image0)
            photo0 = uploaded_file_url0 = fs.url(filename0)
            return render(request, html, {'input_image': uploaded_file_url0, 'bg_image': uploaded_file_url })
        if html=='sharpen.html':
            photo1 = photo
            image1 = cv2.imread(settings.MEDIA_ROOT+photo1.replace("/media","/"))
            filtered = cv2.filter2D(image1, -1, np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]))
            cv2.imwrite("C:/Users/Admin/Desktop/Website1/media/sharp.png", filtered)
            return render(request, 'sharpen.html', {'bg_image': photo, 'output_image': FileSystemStorage().url('sharp.png')})
        # Render the same HTML page with the uploaded image displayed
        return render(request, html, {'bg_image': uploaded_file_url })
    return render(request, html)

def camera(request):
    return uploader(request, 'bg.html')

def image(request):
    return uploader(request, 'image_bg.html')

def back(request):
    global photo, photo0
    photo1 = photo
    photo2 = photo0
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
    p = "C:/Users/Admin/Desktop/Website1"
    flag = True
    def changer(input_image):
        bg_image = cv2.imread(p+photo1)
        height , width, channel = input_image.shape
        RGB = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        # get the result 
        results = selfie_segmentation.process(RGB)

        # extract segmented mask
        mask = results.segmentation_mask

        # it returns true or false where the condition applies in the mask
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.6

        # resize the background image to the same size of the original frame
        bg_image = cv2.resize(bg_image, (width, height))

        # combine frame and background image using the condition
        output_image = np.where(condition, input_image, bg_image)
        cv2.imwrite("C:/Users/Admin/Desktop/Website1/media/input.png",input_image)
        cv2.imwrite("C:/Users/Admin/Desktop/Website1/media/output.png",output_image)
    if photo2 == "":
        cap = cv2.VideoCapture(0)
        while cap.isOpened() and flag:
            _, input_Image = cap.read()
            if not _:
                break
            input_Image = cv2.flip(input_Image, 1)
            changer(input_Image)
            flag = False
        cap.release()
    else:
        input_Image = cv2.imread(p+photo2)
        changer(input_Image)
    
    return render(request, 'bg.html', {'input_image':FileSystemStorage().url('input.png'),'bg_image': photo,'output_image':FileSystemStorage().url('output.png')} )

def cc(request):
    global photo 
    photo1 = photo
    if request.method == 'POST':
        rgb = request.POST.get('rgb')
        rgb = rgb.split(",")
        rgb = [int(i) for i in rgb ]
        rgb.pop()
        n_rgb = request.POST.get('new-color')
        n_rgb = n_rgb.lstrip('#')
        n_rgb = tuple(int(n_rgb[i:i+2], 16) for i in (0, 2, 4))
        img = Image.open(settings.MEDIA_ROOT+photo1.replace("/media","/"))
        img = img.convert("RGB")
        pixel_array = np.array(img)
        rgb_img = pixel_array[..., :3]
        rgb_img[np.all(rgb_img == rgb, axis=-1)] = [n_rgb[0],n_rgb[1],n_rgb[2]]
        pixel_array[..., :3] = rgb_img
        output = Image.fromarray(pixel_array)
        output.save("C:/Users/Admin/Desktop/Website1/media/cco.png")
    return render(request, 'change_color.html', {'bg_image': photo, 'output_image': FileSystemStorage().url('cco.png')})     

def crop1(request):
    global photo
    photo1 = photo
    if request.method == 'POST':
        r = request.POST.get('rectan')
        r = r.split(",")
        r = [int(i) for i in r]
        if r[2] < 0 :
            r[2] *= -1
            r[0] = r[0] - r[2]
        if r[3] < 0 :
            r[3] *= -1
            r[1] = r[1] - r[3]
        image = Image.open(settings.MEDIA_ROOT+photo1.replace("/media","/"))
        cropped_image = image.crop((r[0], r[1], r[0]+r[2], r[1]+r[3]))
        cropped_image.save('C:/Users/Admin/Desktop/Website1/media/crop_output.png')
    return render(request, 'crop.html',{'bg_image': photo, 'output_image': FileSystemStorage().url('crop_output.png')})
