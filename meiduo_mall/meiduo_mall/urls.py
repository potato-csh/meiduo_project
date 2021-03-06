"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # haystack
    url(r'^search/', include('haystack.urls')),

    # users
    url(r'^', include(('users.urls', 'users'), namespace='users')),
    # contents
    url(r'^', include(('contents.urls', 'contents'), namespace='contents')),
    # verifications
    url(r'^', include(('verifications.urls', 'verifications'))),
    # oauth
    url(r'^', include(('oauth.urls', 'oauth'))),
    # areas
    url(r'^', include(('areas.urls', 'areas'))),
    # goods
    url(r'^', include(('goods.urls', 'goods'))),
    # carts
    url(r'^', include(('carts.urls', 'carts'))),
    # orders
    url(r'^', include(('orders.urls', 'orders'))),
    # payment
    url(r'^', include(('payment.urls', 'payment'))),
    # meiduo_admin
    url('^meiduo_admin/', include('meiduo_admin.urls')),

]
