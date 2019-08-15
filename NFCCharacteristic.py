from pybleno import Characteristic
import array
import struct
import sys
import traceback

_monitor = None


class NFCCharacteristic(Characteristic):
    def __init__(self, uuid, monitor):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'write', 'notify'],
            'value': None
        })
        if monitor:
            self._monitor = monitor

        self._updateValueCallback = None

    def Update(self, value):
        self._updateValueCallback(value)

    def onReadRequest(self, offset, callback):
        monitor_detected = (self._monitor.CARD_DETECTED | self._monitor.ID_DETECTED << 1)
        callback(Characteristic.RESULT_SUCCESS, array.array('B', [monitor_detected]))

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        pass
        # self._value = data
        #
        # print('EchoCharacteristic - %s - onWriteRequest: value = %s' % (self['uuid'], [hex(c) for c in self._value]))
        #
        # if self._updateValueCallback:
        #     print('EchoCharacteristic - onWriteRequest: notifying')
        #
        #     self._updateValueCallback(self._value)
        #
        # callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('EchoCharacteristic - onSubscribe')

        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('EchoCharacteristic - onUnsubscribe')

        self._updateValueCallback = None
