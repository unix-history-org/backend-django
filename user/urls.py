from django.urls import include, path

# [POST] /api/user/register - регистрация пользователей принимает POST запрос,
#        ожидаемые параметры: {“login”: строка, “password”: строка} результат токен
# [POST] /api/user/login - точно то-же самое, но другие возможные ошибки
# [POST] /api/user/logout на вход ожидает {“tokken”: строка} делает токен не доступным
# [GET] /api/user/{id} - возвращает информацию о пользователе с id
# [GET] /api/user/permission - данные о правах на запуск ВМ
# [GET] /api/user/me - информация о текущем пользователе
urlpatterns = [
    # path(r'', include('dj_rest_auth.urls')),
    # path(r'', include('dj_rest_auth.registration.urls')),
]
