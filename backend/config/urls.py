"""
URL configuration for Noma Card House project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Debug toolbar
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]

# Customize admin site
admin.site.site_header = 'Noma Card House Admin'
admin.site.site_title = 'Noma Admin'
admin.site.index_title = 'Administration'
