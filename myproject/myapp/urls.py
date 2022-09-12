from django.urls import path

from . import views


urlpatterns = [
    
    path('index', views.index, name="home"),
    path('filesolution', views.filedownloadpage, name='csvfilesolution'),
    path('solutiondownload', views.download_file, name='solutiondownload')
    
]