"""
ASGI config for unixhistory project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

from django.conf import settings

settings.configure()


from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from os_api import urls as os_api_urls




application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(os_api_urls.websocket_urlpatterns),
})