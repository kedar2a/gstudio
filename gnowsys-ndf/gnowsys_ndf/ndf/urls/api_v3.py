from django.conf.urls import patterns, url, include
from rest_framework import routers
from gnowsys_ndf.ndf.views import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
# router.register(r'filehives', views.FileHiveViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
)
