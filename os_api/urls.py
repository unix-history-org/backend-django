from django.conf.urls import url
from django.urls import include, path

from os_api.views import OSListView, OSSSHView

pass
# [GET] /api/os/list - список всех систем
# [GET] /api/os/stack - структурированный список всех систем
# [GET] /api/os/{id} - полная информация о конкретной системе
# [WEBSOCKET] /api/os/{id}/ssh - подключение к ОС по протоколу ssh
# [WEBSOCKET] /api/os/{id}/vnc - данные по vnc протоколу (в душе не ебу, пока, как делать)

urlpatterns = [
    path(r'list/', OSListView.as_view()),
    path(r'<int:pk>/', OSListView.as_view()),

]

websocket_urlpatterns = [
    # url(r'^api/os/(?P<pk>[^/]+)/ssh', OSSSHView.as_asgi()),
    path(r'api/os/<int:pk>/ssh', OSSSHView.as_asgi()),
]