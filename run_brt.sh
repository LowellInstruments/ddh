#!/usr/bin/env bash
source /home/pi/li/ddh/scripts/utils.sh


clear

check_already_running "main_brt"


echo && echo
_pb "###############"
_pb "     DDH BRT   "
_pb "###############"
echo


if [ -f "$FOL_LI"/cfg_brt_nadv.toml ]; then
    _pb "generating $FOL_LI/cfg_brt_nadv.toml for you"
    cp "$FOL_DDH"/settings/cfg_brt_nadv.toml "$FOL_LI"
fi

source "$FOL_VEN"/bin/activate
cd "$FOL_DDH" && "$FOL_VEN"/bin/python main_brt.pyc
