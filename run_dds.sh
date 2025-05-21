#!/usr/bin/env bash
source /home/pi/li/ddh/scripts/utils.sh


echo


# check we need a reboot
if [ -f "$LI_DDH_NEEDS_REBOOT_POST_INSTALL" ]; then
    _pr "DDS was just installed, please reboot"
    exit 0
fi



# for crontab to detect python already running
check_already_running "main_dds_controller"



# start with a clean BLE sheet
_pb "DDS BLE disabling cache from /etc/bluetooth/main.conf"
sudo sed -i '/#Cache = always/c\Cache = no' /etc/bluetooth/main.conf



_pb "DDS BLE delete /var cache entries"
LS_HCI_MACS=$(hciconfig -a | grep "BD Address" | cut -d " " -f 3)
for HM in $LS_HCI_MACS; do sudo rm "/var/lib/bluetooth/$HM"/cache/*; done



_pb "DDS BLE resetting interfaces"
sudo hciconfig hci0 reset 2> /dev/null || _py "cannot reset hci0"
sudo hciconfig hci1 reset 2> /dev/null || _py "cannot reset hci1"



_pb "DDS BLE restarting system service"
sudo systemctl restart bluetooth
sleep 2



_pb "DDS BLE bring interfaces UP"
sudo hciconfig hci0 up 2> /dev/null || _py "cannot UP hci0"
sudo hciconfig hci1 up 2> /dev/null || _py "cannot UP hci1"



_pb "DDS BLE check at least 1 interface OK"
(hciconfig hci0 | grep RUNNING) &> /dev/null; rv0=$?
(hciconfig hci1 | grep RUNNING) &> /dev/null; rv1=$?
if [ $rv0 -ne 0 ]; then _py "hci0 not present"; fi
if [ $rv1 -ne 0 ]; then _py "hci1 not present"; fi
if [ $rv0 -ne 0 ] && [ $rv1 -ne 0 ]; then
    _pr "error: DDS needs at least 1 Bluetooth interface"
    exit 1
fi



_pb "DDS BLE set connection supervision timeout"
touch /tmp/200
echo '200' | sudo tee /sys/kernel/debug/bluetooth/hci0/supervision_timeout 2> /dev/null
echo '200' | sudo tee /sys/kernel/debug/bluetooth/hci1/supervision_timeout 2> /dev/null



_pb "DDS check wi-fi interface is not rf-killed"
sudo rfkill unblock wlan



_pb "DDS set permissions on linux binaries 'date' and 'ifmetric'"
sudo setcap CAP_SYS_TIME+ep /bin/date
sudo setcap 'cap_net_raw,cap_net_admin+eip' /usr/sbin/ifmetric



_pb "DDS activating virtualenv"
sudo chown -R pi:pi "$FOL_DDH"
source "$FOL_VEN"/bin/activate



_pb "DDS run main_qus.py to auto-detect Quectel shield USB ports"
cd "$FOL_DDH" && "$FOL_VEN"/bin/python main_qus.py
QUC=$(cat /tmp/usb_quectel_ctl)



# detect cell shield SIM ID and write it to file
if [ "${QUC}" ]; then
    if [ ! -s "$LI_FILE_ICCID" ]; then
        # the file is zero
        rm "$LI_FILE_ICCID" > /dev/null 2>&1
    fi
    if [ ! -f "$LI_FILE_ICCID" ]; then
        # the file does not exist
        for idx_iccid in {1..5}
        do
            _pb "DDS query Quectel SIM ID on $QUC, attempt #$idx_iccid"
            echo -ne "AT+QCCID\r" > "$QUC"
            sleep 0.1
            timeout 1 cat -v < "$QUC" | grep QCCID > "$LI_FILE_ICCID"
            if [ -s "$LI_FILE_ICCID" ]; then
                # there is something in the file :)
                break
            fi
        done
    fi
fi



echo && echo
_pb "-------------"
_pb "run DDS core "
_pb "-------------"
echo
cd "$FOL_DDH" && "$FOL_VEN"/bin/python main_dds.py
