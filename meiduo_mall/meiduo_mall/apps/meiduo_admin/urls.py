from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
]
