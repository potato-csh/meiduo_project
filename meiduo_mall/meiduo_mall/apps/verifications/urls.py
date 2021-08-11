from django.conf.urls import url
from .views import *

urlpatterns = {
    url(r'^image_codes/(?P<uuid>[\w-]+)/$',ImageCodeView.as_view()),
}