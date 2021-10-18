from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^payment/(?P<order_id>\d+)/$', PaymentView.as_view()),
]
