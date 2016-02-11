import eav
from django.db import models
from django.utils.translation import ugettext as _
from eav.models import Attribute
from macaddress.fields import MACAddressField
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase

from .lib import phone_regex, GestioIPError


class EavBase:
    @staticmethod
    def add_field(fname, ftype):
        try:
            ftype = getattr(Attribute, 'TYPE_%s' % ftype)
        except AttributeError:
            raise GestioIPError(_("Invalid custom field type."))
        Attribute.objects.create(name=fname, datatype=ftype)


class CustomTag(TagBase):
    tag = models.CharField(max_length=50)
    description = models.CharField(max_length=500)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class GestioIPTaG(GenericTaggedItemBase):
    tag = models.ForeignKey(CustomTag,
                            related_name="%(app_label)s_%(class)s_items")


class Client(models.Model):
    # include Fixture for client "DEFAULT"
    name = models.TextField()

    def __str__(self):
        return self.name


class Contact(models.Model):
    client = models.ManyToManyField(Client)
    # one of the fields name or surname must be introduced
    name = models.CharField(blank=True, max_length=254)
    surname = models.CharField(blank=True, max_length=254)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True, help_text="Address")
    phone_number = models.CharField(blank=True, max_length=254, validators=[
        phone_regex])  # validators should be a list
    movil_number = models.CharField(blank=True, max_length=254, validators=[
        phone_regex])  # validators should be a list
    comment = models.CharField(max_length=254)


class GSite(models.Model):
    class Meta:
        app_label = "gestioip"

    client = models.ManyToManyField(Client)
    name = models.CharField(max_length=150)
    tags = TaggableManager(through=GestioIPTaG)

    def __str__(self):
        return self.name


class HostCategory(models.Model):
    # include Fixture (db, fw, server, router, ...)
    name = models.CharField(max_length=150)
    comment = models.CharField(blank=True, max_length=254)

    def __str__(self):
        return self.name


class NetworkCategory(models.Model):
    # include Fixture (prod, pre, dev, test, ...)
    name = models.CharField(max_length=150)
    comment = models.CharField(blank=True, max_length=254)

    def __str__(self):
        return self.name


class CompanyType(models.Model):
    # include Fixture (provider, consulting, supplier, maintenance, ...)
    company_type = models.TextField(
        help_text="Company type like provider (for VLAN Provider, AS Provider"
                  "...), consulting, supplier, maintenance, ...")
    comment = models.CharField(blank=True, max_length=254)

    def __str__(self):
        return self.company_type


class Company(models.Model):
    client = models.ManyToManyField(Client, blank=True)
    contact = models.ManyToManyField(Contact, blank=True)
    company_type = models.ManyToManyField(CompanyType, blank=True)
    name = models.CharField(blank=True, max_length=254)
    address = models.TextField(blank=True, help_text="Address")
    phone_number = models.CharField(blank=True, max_length=254, validators=[
        phone_regex])  # validators should be a list
    fax_number = models.CharField(blank=True, max_length=254, validators=[
        phone_regex])  # validators should be a list
    comment = models.CharField(blank=True, max_length=254)

    # include custom columns

    def __str__(self):
        return self.name


class VLAN(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default="")
    provider = models.ForeignKey(Company, blank=True, null=True)
    number = models.IntegerField()
    name = models.CharField(max_length=254)
    comment = models.CharField(blank=True, max_length=254)
    description = models.TextField(blank=True, help_text="Descriptive text")

    # include custom columns

    def __str__(self):
        return self.name


class VRF(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default="")
    name = models.CharField(max_length=254, blank=False)
    RD = models.CharField(max_length=50, blank=False)
    comment = models.CharField(blank=True, max_length=254)
    description = models.TextField(blank=True, help_text="Descriptive text")

    def __str__(self):
        return self.name


class DNSServerGroup(models.Model):
    #    client = models.ManyToManyField(Clients)
    name = models.CharField(max_length=254)
    comment = models.CharField(blank=True, max_length=254)
    description = models.TextField(blank=True, help_text="Descriptive text")

    def __str__(self):
        return self.name


class DNSServer(models.Model):
    client = models.ManyToManyField(Client)
    ip_address = models.GenericIPAddressField(unique=True,
                                              help_text="Enter an IP Address")
    name = models.CharField(blank=True, max_length=254)
    comment = models.CharField(blank=True, max_length=254)
    description = models.TextField(blank=True, help_text="Descriptive text")
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.ip_address


class NetworkColumnHierarchy(models.Model):
    column_name = models.CharField(unique=True, max_length=150)
    level = models.IntegerField(help_text="Hierarchy level")


class Network(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default="")
    # can a network have multiple VLANs?
    vlan = models.ForeignKey(VLAN, blank=True, null=True)
    dns_server_group = models.ForeignKey(DNSServerGroup, blank=True, null=True)
    site = models.ForeignKey(GSite, blank=True, null=True)
    category = models.ForeignKey(NetworkCategory, blank=True, null=True)
    vrf = models.ForeignKey(VRF, blank=True, null=True,
                            related_name="%(app_label)s_%(class)s_name")
    RD = models.ForeignKey(VRF, blank=True, null=True,
                           related_name="%(app_label)s_%(class)s_RD")
    ip_address = models.GenericIPAddressField(help_text="Enter an IP Address")
    mask = models.IntegerField(default=24,
                               help_text="Enter a Mask/Prefix Length")
    rootnet = models.BooleanField()
    utilization = models.SmallIntegerField(default=0,
                                           help_text="Network utilization")
    description = models.TextField(blank=True, help_text="Descriptive text")
    comment = models.CharField(blank=True, max_length=254,
                               help_text="Short comment")
    tags = TaggableManager(through=GestioIPTaG)

    # include custom columns

    def __str__(self):
        return u'%s/%s' % (self.ip_address, self.mask)


class SNMPGroup(models.Model, EavBase):
    client = models.ManyToManyField(Client)
    version = models.SmallIntegerField(default=2, help_text="SNMP version")
    name = models.CharField(unique=True, max_length=254)
    comment = models.CharField(blank=True, max_length=254,
                               help_text="Short comment")
    # Depending of the snmp version, cummunity or auth password must
    # not be blank
    community = models.CharField(blank=True, max_length=254,
                                 help_text="SNMPv1/2c community string")
    security_level = models.CharField(blank=True, max_length=25,
                                      help_text="SNMPv3 security level")
    auth_algorithm = models.CharField(blank=True, max_length=25,
                                      help_text="SNMPv3 authentication "
                                                "algorithm")
    auth_password = models.CharField(blank=True, max_length=254,
                                     help_text="SNMPv3 authentication "
                                               "password")
    priv_algorithm = models.CharField(blank=True, max_length=25,
                                      help_text="SNMPv3 privacy algorithm")
    priv_password = models.CharField(blank=True, max_length=254,
                                     help_text="SNMPv3 privacy password")

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(unique=True, max_length=254)
    image = models.ImageField(upload_to=None, height_field=None,
                              width_field=None)
    comment = models.CharField(blank=True, max_length=254,
                               help_text="Short comment")

    def __str__(self):
        return self.image


class OS(models.Model):
    name = models.CharField(unique=True, max_length=254)
    image = models.ImageField(upload_to=None, height_field=None,
                              width_field=None)
    comment = models.CharField(blank=True, max_length=254,
                               help_text="Short comment")

    def __str__(self):
        return self.image


class Asset(models.Model):
    client = models.ManyToManyField(Client)
    site = models.ForeignKey(GSite, blank=True, null=True)
    name = models.CharField(unique=True, max_length=254)
    hostname = models.CharField(blank=True, max_length=254,
                                help_text="hostname")
    category = models.ForeignKey(HostCategory, blank=True, null=True)
    snmp_group = models.ForeignKey(SNMPGroup, blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True)
    os = models.ForeignKey(OS, blank=True, null=True)
    #    rack = models.ForeignKey(Rack, blank=True, null=True)
    #    rack_unit = models.ForeignKey(RackUnit, blank=True, null=True)
    serial_number = models.CharField(blank=True, max_length=254,
                                     help_text="SN")
    comment = models.CharField(blank=True, max_length=254,
                               help_text="Short comment")
    description = models.TextField(blank=True, help_text="Descriptive text")
    descr_snmp = models.TextField(blank=True, help_text="Descriptive text")
    tags = TaggableManager(blank=True, through=GestioIPTaG)

    def __str__(self):
        return self.ip_address


class AppImages(models.Model):
    # Images for IP.url
    name = models.CharField(unique=True, max_length=254)
    image = models.ImageField(upload_to=None, height_field=None,
                              width_field=None)
    comment = models.CharField(blank=True, max_length=254,
                               help_text="Short comment")

    def __str__(self):
        return self.image


class IP(models.Model, EavBase):
    network = models.ForeignKey(Network)
    # shared with Asset....
    asset = models.ForeignKey(Asset, blank=True, null=True,
                              on_delete=models.CASCADE)
    site = models.ForeignKey(GSite, blank=True, null=True)
    category = models.ForeignKey(HostCategory, blank=True, null=True)
    snmp_group = models.ForeignKey(SNMPGroup, blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True)
    os = models.ForeignKey(OS, blank=True, null=True)
    serial_number = models.CharField(blank=True, max_length=254,
                                     help_text="SN")
    # one of hostname or dns_name should be mandatory
    hostname = models.CharField(blank=True, max_length=254,
                                help_text="hostname")
    dns_name = models.TextField(blank=True,
                                help_text="DNS entries for this IP address")
    #    update_type = models.ForeignKey(UpdateType, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    # readonly for dns_name - update only by discovery? or check user input
    # with DNS query - notify errors
    description = models.TextField(blank=True, help_text="Descriptive text")
    comment = models.CharField(blank=True, max_length=254,
                               help_text="Short comment")
    domain = models.CharField(blank=True, max_length=254,
                              help_text="Short comment")
    cnames = models.TextField(blank=True, help_text="List of DNS CNAME "
                                                    "defined for this IP")

    mac = MACAddressField(null=True, blank=True, help_text="MAC address")
    # linked_ip contains a list of IPs to which this IP is linked to
    linked_ip = models.ManyToManyField('self', blank=True)
    # user should also be able to introduce a string for the case that there is
    #  no app image available
    url = models.TextField(blank=True,
                           help_text="IP specific links to external apps like "
                                     "Nagios, Cacti, ...")

    ifAlias = models.CharField(blank=True, max_length=254, help_text="ifAlias")
    ifDescr = models.CharField(blank=True, max_length=254, help_text="ifDescr")
    cm_enabled = models.BooleanField(default=False)
    # here also configuration management (cm) related values or specific table
    # for cm values?
    ping_status = models.NullBooleanField()
    ping_last_checked = models.DateField(null=True)
    tags = TaggableManager(through=GestioIPTaG)

    def __str__(self):
        return self.ip_address


class Line(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    provider = models.ForeignKey(Company, blank=True, null=True)
    phone_number = models.CharField(max_length=254, validators=[phone_regex],
                                    blank=True)  # validators should be a list
    number = models.IntegerField(unique=True, blank=False)
    name = models.CharField(unique=True, max_length=254)
    comment = models.CharField(blank=True, max_length=254,
                               help_text="Short comment")
    description = models.TextField(blank=True, help_text="Descriptive text")
    tags = TaggableManager(through=GestioIPTaG)

    # custom columns

    def __str__(self):
        return self.name


eav.register(IP)
eav.register(Network)