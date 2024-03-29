import re

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.conf import urls

from maintenancemode.models import Maintenance, IgnoredURL

urls.handler503 = 'maintenancemode.views.defaults.temporary_unavailable'
urls.__all__.append('handler503')


class MaintenanceModeMiddleware(object):
    def process_request(self, request):
        site = Site.objects.get_current()

        """
        Get the maintenance mode from the database.
        If a Maintenance value doesn't already exist in the database, we'll create one.
        "has_add_permission" and "has_delete_permission" are overridden in admin
        to prevent the user from adding or deleting a record, as we only need one
        to affect multiple sites managed from one instance of Django admin.
        """
        try:
            maintenance = Maintenance.objects.get(site=site)
        except Maintenance.DoesNotExist:
            # Create new entry for current site
            maintenance = Maintenance.objects.create(site=site, is_being_performed=False)
        except Maintenance.MultipleObjectsReturned:
            """In a perfect world this should never occur. But the world is rarely perfect
               Check that Maintenance is being performed and select first one"""
            jobs = Maintenance.objects.filter(site=site, is_being_performed=True)
            if jobs.exists():
                maintenance = jobs[0]
            else:
                return None

        # Allow access if maintenance is not being performed
        if not maintenance.is_being_performed:
            return None

        # Allow access if remote ip is in INTERNAL_IPS
        if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return None

        # Allow access if the user doing the request is logged in and a
        # staff member.
        if hasattr(request, 'user') and request.user.is_staff:
            return None

        # Check if a path is explicitly excluded from maintenance mode
        urls_to_ignore = IgnoredURL.objects.filter(maintenance=maintenance)
        ignore_urls = tuple([re.compile(r'%s' % str(url.pattern)) for url in urls_to_ignore])
        for url in ignore_urls:
            if url.match(request.path_info):
                return None

        # Otherwise show the user the 503 page
        resolver = urlresolvers.get_resolver(None)

        callback, param_dict = resolver._resolve_special('503')
        return callback(request, **param_dict)
