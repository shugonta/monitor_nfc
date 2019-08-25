from pybleno import Characteristic
import array
import struct
import sys
import traceback


class MonitorCharacteristic(Characteristic):
    def __init__(self, uuid, monitor):
        self._monitor = None
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'notify'],
            'value': None
        })
        if monitor:
            self._monitor = monitor

        self._updateValueCallback = None

    def Update(self, value):
        if self._updateValueCallback is not None:
            self._updateValueCallback(value)

    def onReadRequest(self, offset, callback):
        monitor_detected = self._monitor.state.pack()
        callback(Characteristic.RESULT_SUCCESS, array.array('B', monitor_detected))

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        pass
        # self._value = data
        #
        # print('MonitorCharacteristic - %s - onWriteRequest: value = %s' % (self['uuid'], [hex(c) for c in self._value]))
        #
        # if self._updateValueCallback:
        #     print('MonitorCharacteristic - onWriteRequest: notifying')
        #
        #     self._updateValueCallback(self._value)
        #
        # callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('MonitorCharacteristic - onSubscribe')
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('MonitorCharacteristic - onUnsubscribe')
        self._updateValueCallback = None
