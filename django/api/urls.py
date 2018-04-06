from django.conf.urls import include, url
from rest_auth import urls as rest_auth_urls
from rest_framework import routers

from .contributors import ContributorViewSet
from .issues import IssueViewSet, PrintIssueViewSet
from .legacy_viewsets import ProdStoryViewSet
from .permissions import PermissionViewSet
from .photos import ImageFileViewSet
from .stories import StoryTypeViewSet, StoryViewSet
from .upload_image import FileUploadViewSet

router = routers.DefaultRouter()
router.register(r'images', ImageFileViewSet)
router.register(r'issues', IssueViewSet)
router.register(r'pdfs', PrintIssueViewSet)
router.register(r'contributors', ContributorViewSet)
router.register(r'stories', StoryViewSet, 'story')
router.register(r'storytypes', StoryTypeViewSet)
router.register(r'legacy', ProdStoryViewSet, 'legacy')
router.register(r'permissions', PermissionViewSet)
router.register(r'upload', FileUploadViewSet, 'upload')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(
        r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
    url(r'^rest-auth/', include(rest_auth_urls)),
]
