from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from django.core.asgi import get_asgi_application

from .guacdproxy import GuacamoleConsumer

application = ProtocolTypeRouter({
    # Django->http is not added automatically in Channels 3.0
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('tunnelws/ticket/<uuid:ticket>/', GuacamoleConsumer.as_asgi()),
        ])
    ),
})
