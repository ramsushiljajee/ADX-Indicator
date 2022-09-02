from django.urls import path

from . import views


urlpatterns = [
    
    path('', views.index, name="home"),
    path('filesolution', views.filedownloadpage, name='csvfilesolution'),
    path('solutiondownload', views.downloadfile, name='solutiondownload'),
    path('execute', views.displayplot, name='execute')
]