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
        ssid_cnt = len(self._config.getSSIDList())
        callback(Characteristic.RESULT_SUCCESS, array.array('B', [ssid_cnt]))

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data

        print('MonitorCharacteristic - %s - onWriteRequest: value = %s' % (self['uuid'], [hex(c) for c in self._value]))

        # if self._updateValueCallback:
        #     print('MonitorCharacteristic - onWriteRequest: notifying')
        #
        #     self._updateValueCallback(self._value)
        #
        # callback(Characteristic.RESULT_SUCCESS)
