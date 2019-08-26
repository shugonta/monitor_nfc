from pybleno import Characteristic
import array
import struct
import sys
import traceback


class SSIDCharacteristic(Characteristic):
    def __init__(self, uuid, config):
        self._config = config
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'write'],
            'value': None
        })

    def onReadRequest(self, offset, callback):
        ssid_list = ",".join(self._config.getSSIDList())
        callback(Characteristic.RESULT_SUCCESS, array.array('B', ssid_list.encode("utf-8")))

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        ssid_list = data.decode("utf-8")
        self._config.setSSIDList(ssid_list.split(","))

        # if self._updateValueCallback:
        #     print('MonitorCharacteristic - onWriteRequest: notifying')
        #
        #     self._updateValueCallback(self._value)
        #
        callback(Characteristic.RESULT_SUCCESS)
