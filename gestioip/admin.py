from django.contrib import admin

from gestioip import models


class IPAdmin(admin.ModelAdmin):
    pass


class NetworkAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.IP, IPAdmin)
admin.site.register(models.Network, NetworkAdmin)

auto_classes = ["VLAN", "Client", "Contact", "GSite", "HostCategory",
                "NetworkCategory", "CompanyType", "Company", "VRF",
                "DNSServerGroup", "DNSServer", "NetworkColumnHierarchy",
                "SNMPGroup", "Manufacturer", "OS", "Asset", "AppImages",
                "Line"]

for each in auto_classes:
    admin.site.register(getattr(models, each))
