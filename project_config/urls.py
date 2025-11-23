"""
URL configuration for VoteWise project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Core URLs
    path('', include('apps.core.urls')),
    
    # Authentication URLs
    path('auth/', include('apps.accounts.urls')),
    
    # Elections URLs
    path('elections/', include('apps.elections.urls')),
    
    # Administration URLs
    path('administration/', include('apps.administration.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)