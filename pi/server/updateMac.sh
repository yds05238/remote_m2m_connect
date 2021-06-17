#! /bin/bash

mac=$(hciconfig hci0 | awk '/BD Address: /{print $3}')
if [ "$mac" != NULL ] ; then
	echo $mac
	a="MY_ADDRESS"
	b="\"$mac\""
	sed -i -e "s/\($a = \).*/\1$b/"  update_device_config.py
fi
#echo $mac
