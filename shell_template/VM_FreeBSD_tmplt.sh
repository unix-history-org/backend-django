cp /home/verdgil/aqemu/freebsd_tmpl /home/verdgil/www/unix-history.org/vm_hard_tmp/freebsd_%s
/usr/bin/qemu-system-x86_64  -smp 2 -cpu SandyBridge -machine accel=kvm -m 1024 -hda "/home/verdgil/www/unix-history.org/vm_hard_tmp/freebsd_%s" -boot order=cd,menu=off -net nic,macaddr=00:1e:a2:58:80:7f -net user -net user,hostfwd=tcp::%s-:22 -rtc base=localtime -name "FreeBSD" $*



timeout 15m rm /home/verdgil/www/unix-history.org/vm_hard_tmp/freebsd_%s