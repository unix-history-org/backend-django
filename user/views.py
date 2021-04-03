from dj_rest_auth.views import LoginView
from rest_framework.response import Response


class CustomLoginView(LoginView):

    def post(self, request, *args, **kwargs):
        self.request = request
        if "login" in self.request.data:
            self.request.data["username"] = self.request.data["login"]
        if "login" in self.request.data:
            self.request.data["email"] = self.request.data["login"]
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=False)
        try:
            self.login()
        except KeyError as key_err: # HACK
            return Response(data={
                "status": "error",
                "info": {
                    "code": "user_not_found"
                },
                "payload": {}
            })
        resp = self.get_response()
        return resp
