import subprocess

from channels.generic.websocket import WebsocketConsumer
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from os_api import utils
from os_api.models import OS, EMULATIONCHOICE, Permiss, SSHTYPECHOICE
from os_api.serializers import OSListSerializer


class OSListView(ListAPIView):
    serializer_class = OSListSerializer
    # pagination_class = None

    def get_queryset(self):
        os_list_obj = OS.objects.filter(is_active=True)
        return os_list_obj

    def list(self, request, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = OSListSerializer(queryset, many=True)
        return Response(serializer.data)


class OSSSHView(WebsocketConsumer):
    def connect(self):
        os_id = self.scope['url_route']['kwargs']['pk']
        os_obj = OS.objects.filter(pk=os_id)
        if len(os_obj) > 0:
            os_obj = os_obj[0]
            if os_obj.ssh_enable:
                self.os_obj = os_obj
                self.accept()
                self.send(text_data="Подключенно, подождите пару минут")
                if os_obj.emulation_type == EMULATIONCHOICE.QEMU_KVM:
                    self.disk_name = utils.get_random_string(16)
                    self.port_num = utils.get_random_port()
                    start_string = (os_obj.start_config %
                                    (self.disk_name, self.disk_name, str(self.port_num))).split('\r\n')
                    if os_obj.ssh_type == SSHTYPECHOICE.SSH:
                        cp_ret_code = subprocess.call(start_string[0].split(' '))
                        if cp_ret_code == 0:
                            self.qemu_proc = subprocess.Popen(start_string[1].split(' '))
                    self.send(start_string)
            else:
                self.close()
        else:
            self.close()

    def receive(self, text_data=None, bytes_data=None):
        if text_data.startswith("/name"):
            self.username = text_data[5:].strip()
            self.send(text_data="[set your username to %s]" % self.username)
        else:
            self.send(text_data=self.username + ": " + text_data)

    def disconnect(self, message):
        pass