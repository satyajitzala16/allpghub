from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from pgbooking import views

urlpatterns = [
    path('admin/', admin.site.urls),
     path('',include('pgbooking.urls'))

] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
