from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('about.html', views.about, name = 'about'),
    path('pricing.html', views.pricing, name = 'pricing'),
    path('contact.html', views.contact, name = 'contact'),
    path('background/', views.background,),
    path('back/', views.back, name='back'),
    path('camera/', views.camera, name='cam'),
    path('imagebg/', views.image, name='imagebg'),
    path('change_color/', views.change_color, name='change_color'),
    path('cc/', views.cc, name='cc'),
    path('crop/', views.crop, name='crop'), 
    path('crop1/', views.crop1, name='crop1'),
    path('sharpen/', views.sharpen_image),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
