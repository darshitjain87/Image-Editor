from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import io
import base64
from datetime import datetime
import os
import cv2
import numpy as np
import mediapipe as mp  

path = settings.MEDIA_ROOT
fs = FileSystemStorage()
# Create your views here.
def index(request):
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

def pricing(request):
    return render(request,'pricing.html')

def privacy(request):
    return render(request,'privacy.html')

@csrf_exempt
def captured(request):
    return render(request, 'capture.html')

@csrf_exempt
def image(request):
    return uploader(request, 'image_bg.html')

@csrf_exempt
def crop(request):
    return uploader(request, 'crop.html')
    
@csrf_exempt    
def change_color(request):
    return uploader(request, 'change_color.html')

@csrf_exempt
def sharpen_image(request):
    return uploader(request, 'sharpen.html')

def extension_check(photo):
    ext = os.path.splitext(photo.name)[1]
    if ext not in ['.png', '.jpg', '.jpeg', '.svg']:
        return True

@csrf_exempt
def uploader(request, html):
    global photo, photo0
    photo0 = "" 
    context = dict()
    if request.method == 'POST' and request.FILES.get('image'):
        # Process the uploaded image
        uploaded_image = request.FILES['image']
        if extension_check(uploaded_image):
            return render(request, html,{'error':"Invalid File Type"})
        filename = fs.save(uploaded_image.name, uploaded_image)
        photo = uploaded_file_url = fs.url(filename)
        context = {'bg_image': uploaded_file_url }
        if html=="image_bg.html":
            uploaded_image0 = request.FILES['image0']
            if extension_check(uploaded_image0):
                return render(request, html,{'error':"Invalid File Type"})
            filename0 = fs.save(uploaded_image0.name, uploaded_image0)
            photo0 = fs.url(filename0)
            context = {'input_image': fs.url(filename0), 'bg_image': uploaded_file_url }
        if html=='sharpen.html':
            photo1 = photo
            image1 = cv2.imread(path+photo1.replace("/media","/"))
            filtered = cv2.filter2D(image1, -1, np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]))
            cv2.imwrite(path+"/sharp.png", filtered)
            context = {'bg_image': photo, 'output_image': fs.url('sharp.png')}
    return render(request, html,context)


@csrf_exempt
def back(request):
    global photo, photo0
    photo1 = photo
    photo2 = photo0
    input_Image = cv2.imread(path+photo2.replace("media/",""))
    bg_image = cv2.imread(path+photo1.replace("media/",""))
    output_image = perform_background_removal(input_Image,bg_image)
    cv2.imwrite(path+"/input.png",input_Image)
    cv2.imwrite(path+"/output.png",output_image)
    return render(request, 'image_bg.html', {'input_image':fs.url('input.png'),'bg_image': photo,'output_image':fs.url('output.png')} )

@csrf_exempt
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
        img = Image.open(path+photo1.replace("/media","/"))
        img = img.convert("RGB")
        pixel_array = np.array(img)
        rgb_img = pixel_array[..., :3]
        rgb_img[np.all(rgb_img == rgb, axis=-1)] = [n_rgb[0],n_rgb[1],n_rgb[2]]
        pixel_array[..., :3] = rgb_img
        output = Image.fromarray(pixel_array)
        output.save(path+"/cco.png")
    return render(request, 'change_color.html', {'bg_image': photo, 'output_image': fs.url('cco.png')})     

@csrf_exempt
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
        image = Image.open(path+photo1.replace("/media","/"))
        cropped_image = image.crop((r[0], r[1], r[0]+r[2], r[1]+r[3]))
        cropped_image.save(path+'/crop_output.png')
    return render(request, 'crop.html',{'bg_image': photo, 'output_image': fs.url('crop_output.png')})

@csrf_exempt
def process_image(request):
    if request.method == 'POST':   
        image_data1 =  request.POST.get('image_data')
        bg_image = request.FILES.get('bg_image')
        if image_data1 and bg_image:
            image_data2 = base64.b64decode(image_data1.split(',')[1])
            image = Image.open(io.BytesIO(image_data2))
            image_np = np.array(image)
            bg_image_pil = Image.open(bg_image)
            bg_image_cv2 = np.array(bg_image_pil)
            
            # background removal logic using Mediapipe
            processed_image_np = perform_background_removal(image_np,bg_image_cv2)

            processed_image = Image.fromarray(processed_image_np)
            buffered = io.BytesIO()
            processed_image.save(buffered, format='JPEG')
            processed_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return JsonResponse({'processed_image': processed_image_base64})

    return JsonResponse({'error':"Error"})

def perform_background_removal(image_np, bg):
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

    RGB = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

    # Get the result
    results = selfie_segmentation.process(RGB)

    # Extract segmented mask
    mask = results.segmentation_mask

    # Define a condition for the mask
    condition = np.stack((mask,) * 3, axis=-1) > 0.6

    # Replace the background with a different image (e.g., a custom background)
    custom_bg_image = cv2.resize(bg, (image_np.shape[1], image_np.shape[0]))

    # Combine the images using the condition
    try:
        processed_image_np = np.where(condition, image_np, custom_bg_image)
    except Exception as e:
        processed_image_np = np.where(condition, image_np, custom_bg_image[:, :, :3])
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    cv2.imwrite(path+f"/output_{timestamp}.png",processed_image_np)
    
    return processed_image_np
