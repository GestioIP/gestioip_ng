from tastypie.authentication import SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from gestioip.models import IP


class IPResource(ModelResource):
    class Meta:
        queryset = IP.objects.all()
        resource_name = 'IP'
        authorization = DjangoAuthorization()
        authentication = SessionAuthentication()
