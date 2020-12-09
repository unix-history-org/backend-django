import subprocess
from time import sleep

from channels.generic.websocket import WebsocketConsumer
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from os_api import utils
from os_api.models import OS, EMULATIONCHOICE, Permiss, SSHTYPECHOICE
from os_api.serializers import OSListSerializer
import paramiko


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
                                    (self.disk_name, self.disk_name, str(self.port_num),
                                     self.disk_name)).split('\r\n')
                    if os_obj.ssh_type == SSHTYPECHOICE.SSH:
                        cp_ret_code = subprocess.call(start_string[0].split(' '))
                        if cp_ret_code == 0:
                            self.qemu_proc = subprocess.Popen(start_string[1].split(' '))
                            self.send("Запущено, ожидаем включения")
                            # sleep(1*30)
                            self.send(("НЕ РАБОТАЕТ ФРОНТОВАЯ ЧАСТЬ, СОКЕТ РВЁТСЯ, " +
                                      "ВЫ МОЖЕТЕ ПОДКЛЮЧИТСЯ ПО SSH К ТЕСТОВОВ СИСТЕМЕ КОМАНДОЙ ssh root@unix-history.org:%s " +
                                      "Пароль - uh") % (self.port_num))
                            # stdin, stdout, stderr = client.exec_command('ls -l')
                            # data = stdout.read() + stderr.read()
                    self.send(start_string[1])
            else:
                self.close()
        else:
            self.close()

    def receive(self, text_data=None, bytes_data=None):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname="127.0.0.1", username="root", password="uh", port=self.port_num)
        if text_data is not None:
            print(text_data)
            stdin, stdout, stderr = self.client.exec_command(text_data)
            self.send(stdout.read() + stderr.read())

    def disconnect(self, message):
        if self.qemu_proc is not None:
            self.qemu_proc.kill()
            stop_config = (self.os_obj.stop_config % (self.disk_name)).split('\r\n')
            rm_popen = subprocess.call(stop_config[0].split(' '))
            self.send(rm_popen)
        self.close()
