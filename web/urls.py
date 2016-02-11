from django.conf.urls import url, include
from django.contrib import admin
from tastypie.api import Api

from gestioip.api import IPResource

ip_resource = IPResource()
v1_api = Api(api_name='v1')
v1_api.register(ip_resource)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'api/', include(v1_api.urls)),
]
