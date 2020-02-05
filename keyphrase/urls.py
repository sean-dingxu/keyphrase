"""keyphrase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from app01 import views as app01_views  # new

urlpatterns = [
                  path('', app01_views.indexPage),  # new
                  path('admin/', admin.site.urls),
                  path('search/', app01_views.search),
                  path('homepage/', app01_views.indexPage),  # new
                  path('pdfList/', app01_views.pdfList),
                  path('keyPhraseList/', app01_views.keyPhraseList),
                  path('searchPage/', app01_views.searchPage),
                  path('pdfListByKeyPhrase/', app01_views.pdfListByKeyPhrase),
                  path('keyPhraseWordCloud/', app01_views.keyPhraseWordCloud),


              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
