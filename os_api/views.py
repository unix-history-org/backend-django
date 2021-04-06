import random
import re
import socket
import subprocess
import time
from time import sleep
import ctypes

import paramiko


from channels.generic.websocket import WebsocketConsumer
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
class OSSSHView(WebsocketConsumer):
    def __init__(self):
        super(OSSSHView, self).__init__()
        self.client = None
        self.qemu_proc = None
        self.os_obj = None
        self.disk_name = None
        self.port_num = None
        self.mac = None

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
                    self.random_mac()
                    start_string = (os_obj.start_config %
                                    (self.disk_name, self.disk_name, self.mac, str(self.port_num),
                                     self.disk_name)).split('\r\n')
                    if os_obj.ssh_type == SSHTYPECHOICE.SSH:
                        cp_ret_code = subprocess.call(start_string[0].split(' '))
                        if cp_ret_code == 0:
                            self.qemu_proc = subprocess.Popen(start_string[1].split(' '))
                            self.send("Запущено, ожидаем включения")
                            self.socket_sleep(60)
                            self.send("READY")
                            self.ssh_connect()
            else:
                self.close()
        else:
            self.close()

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
            self.ssh = self.client.invoke_shell()
        except:
            self.send("Unknown err")

    def receive(self, text_data=None, bytes_data=None):
        try:
            self.ssh.send(text_data)
            self.ssh.settimeout(5)
            output = ""
            while True:
                try:
                    page = self.ssh.recv(10**5).decode("ascii")
                    output += page
                    time.sleep(0.5)
                except socket.timeout:
                    break
                if "More" in page:
                    self.ssh.send(" ")
            output = re.sub(" +--More--| +\x08+ +\x08+", "\n", output)
            output = re.sub("\r", "\n", output)
            self.send(output)
        except Exception as e:
            self.send("Unknown err")

    def disconnect(self, message):
        if self.qemu_proc is not None:
            self.qemu_proc.kill()
            stop_config = (self.os_obj.stop_config % (self.disk_name)).split('\r\n')
            rm_popen = subprocess.call(stop_config[0].split(' '))
            self.send(rm_popen)
        self.close()

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

    def socket_sleep(self, seconds):
        for _ in range(seconds * 1000):
            libc = ctypes.CDLL('libc.so.6')
            libc.usleep(1000)
            self.send(".")
