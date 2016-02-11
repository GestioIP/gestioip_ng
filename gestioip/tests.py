from django.test import TestCase
from eav.models import Attribute
from gestioip.models import IP


class IPTestCase(TestCase):
    def setUp(self):

        Attribute.objects.create(name="color", datatype=Attribute.TYPE_TEXT)
        Attribute.objects.create(name='weight', datatype=Attribute.TYPE_FLOAT)
        ip = IP(name="foo", address="192.168.1.1")
        ip.eav.color = "red"
        ip.eav.color = 23.3
        ip.save()

    def test_custom_fields(self):
        ip = IP.objects.get(name="foo")
        self.assertEqual(ip.eav.color, 'red')
        self.assertEqual(ip.eav.weight, 23.3)