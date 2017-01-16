from django.conf.urls import url,include,handler404,handler500
from lagou import views


urlpatterns = [
    url(r'^index/$',views.index,name='index'),
    url(r'^about/$',views.about,name='about'),
    url(r'^author/$',views.author,name='author'),
    url(r'^userinfo/$',views.userinfo,name='userinfo'),
]
handler404 = 'lagou.views.page_not_found'