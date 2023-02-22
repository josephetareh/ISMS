from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("schedule/", include('staff_schedule.urls', namespace='schedule')),
    path('', include('user_configuration.urls', namespace='user_configuration')),
    path("my-tasks/", include('tasks.urls', namespace='my-tasks')),
    path('__debug__/', include('debug_toolbar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, doument_root=settings.MEDIA_ROOT)
