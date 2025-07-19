from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class HydroNexusAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = _("HydroNexus Africa Admin Portal")

    # Text to put in each page's <h1> (and above login form).
    site_header = _("HydroNexus Africa Administration")

    # Text to put at the top of the admin index page.
    index_title = _("Welcome to HydroNexus Africa Water Quality Monitoring")

    # URL for the "View site" link at the top of each admin page.
    site_url = "/"

# Create custom admin site instance
admin_site = HydroNexusAdminSite(name='hydronexus_admin') 