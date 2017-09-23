""" Urls that are only used in development.  """
from debug_toolbar import urls as debug_toolbar_urls
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from .urls import urlpatterns

experiments = [
    url(r'^editor/', TemplateView.as_view(template_name='editor.html')),
    url(r'^prodsys/', TemplateView.as_view(template_name='prodsys.html')),
]

urlpatterns = [
    url(r'^__debug__/', include(debug_toolbar_urls)),  # django debug toolbar
    url(r'^dev/', include(experiments)),
    *urlpatterns,
    # serve media files from development server
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
