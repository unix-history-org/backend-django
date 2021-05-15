import random
import subprocess
import ctypes

import paramiko


from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from rest_framework.generics import ListAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response

from os_api import utils
from os_api.models import OS, EMULATIONCHOICE, Permiss, SSHTYPECHOICE
from os_api.serializers import OSListSerializer


class OSListView(ListAPIView, RetrieveModelMixin):
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

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs.keys():
            instance = self.get_object()
            instance.read = True
            instance.save()
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request)


# TODO: Rewrite this fucking shit
class OSSSHView(AsyncWebsocketConsumer):
    def __init__(self):
        super(OSSSHView, self).__init__()
        self.ready = False
        self.client = None
        self.qemu_proc = None
        self.os_obj = None
        self.disk_name = None
        self.port_num = None
        self.mac = None

    async def send(self, text_data=None, bytes_data=None, close=False):
        text_data_new = text_data
        if text_data_new is not None and text_data != "":
            text_data_new.replace("\n", "<br>")
            text_data_new += "<br>"
        await super().send(text_data_new, bytes_data, close)

    async def connect(self):
        os_id = self.scope['url_route']['kwargs']['pk']
        os_obj = OS.objects.filter(pk=os_id)
        if len(os_obj) > 0:
            os_obj = os_obj[0]
            if os_obj.ssh_enable:
                self.os_obj = os_obj
                await self.accept()
                await self.send(text_data="Подключено, подождите пару минут")
                if os_obj.emulation_type == EMULATIONCHOICE.QEMU_KVM:
                    self.disk_name = utils.get_random_string(16)
                    self.port_num = utils.get_random_port()
                    self.random_mac()
                    start_string = (os_obj.start_config %
                                    (self.disk_name, self.disk_name, self.mac, str(self.port_num),
                                     self.disk_name)).split('\r\n')
                    print(start_string)
                    if os_obj.ssh_type == SSHTYPECHOICE.SSH:
                        cp_ret_code = subprocess.call(start_string[0].split(' '))
                        if cp_ret_code == 0:
                            self.qemu_proc = subprocess.Popen(start_string[1].split(' '))
                            await self.send("Запущено, ожидаем включения")
                            await self.send("Просто ждите...")
                            await self.send(f"Около {self.os_obj.wait_time} секунд")
                            await self.socket_sleep(self.os_obj.wait_time)
                            await self.send("Можете начинать")
                            self.ready = True
            else:
                await self.close()
        else:
            await self.close()

    def ssh_connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname="127.0.0.1",
                                username="root",
                                password="uh",
                                port=self.port_num,
                                look_for_keys=False,
                                allow_agent=False)
        except Exception as e:
            print(e)
            await self.send("Unknown err")

    async def receive(self, text_data=None, bytes_data=None):
        if not self.ready:
            await self.send("Ещё не всё")
            return
        if text_data == "":
            await self.send("")
        else:
            try:
                self.ssh_connect()
                # ssh = self.client.invoke_shell()
                # self.ssh.settimeout(5)
                stdin, stdout, stderr = self.client.exec_command(text_data)
                output_str = (
                    stdout.read().decode("utf-8") +
                    "\n\n" +
                    stderr.read().decode("utf-8")
                ).replace("\n", "<br>")
                await self.send(output_str)
            except Exception as e:
                print(e)
            finally:
                self.client.close()

    async def disconnect(self, message):
        await super(OSSSHView, self).disconnect(message)
        if self.qemu_proc is not None:
            self.qemu_proc.kill()
            stop_config = (self.os_obj.stop_config % (self.disk_name)).split('\r\n')
            rm_popen = subprocess.call(stop_config[0].split(' '))
            await self.send(str(rm_popen))
        await self.close()

    def random_mac(self, emu_type="qemu"):
        """Generate a random MAC address.
        00-16-3E allocated to xensource
        52-54-00 used by qemu/kvm
        The OUI list is available at http://standards.ieee.org/regauth/oui/oui.txt.
        The remaining 3 fields are random, with the first bit of the first
        random field set 0.
        >>> randomMAC().startswith("00:16:3E")
        True
        >>> randomMAC("foobar").startswith("00:16:3E")
        True
        >>> randomMAC("xen").startswith("00:16:3E")
        True
        >>> randomMAC("qemu").startswith("52:54:00")
        True
        @return: MAC address string
        """
        ouis = {'xen': [0x00, 0x16, 0x3E], 'qemu': [0x52, 0x54, 0x00]}

        try:
            oui = ouis[emu_type]
        except KeyError:
            oui = ouis['xen']

        mac = oui + [
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)]
        ret_mac = ':'.join(map(lambda x: "%02x" % x, mac))
        self.mac = ret_mac
        return ret_mac

    async def socket_sleep(self, seconds):
        for _ in range(seconds * 100):
            libc = ctypes.CDLL('libc.so.6')
            libc.usleep(10000)
            await self.send("")
