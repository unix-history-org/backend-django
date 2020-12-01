from django.urls import include, path

from os_api.views import OSListView

pass
# [GET] /api/os/list - список всех систем
# [GET] /api/os/stack - структурированный список всех систем
# [GET] /api/os/{id} - полная информация о конкретной системе
# [WEBSOCKET] /api/os/{id}/ssh - подключение к ОС по протоколу ssh
# [WEBSOCKET] /api/os/{id}/vnc - данные по vnc протоколу (в душе не ебу, пока, как делать)

urlpatterns = [
    path(r'list/', OSListView.as_view()),
    # path(r'list/', include('dj_rest_auth.registration.urls')),
]

