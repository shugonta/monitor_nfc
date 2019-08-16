from pybleno import *
import sys
import signal
from NFCCharacteristic import *
from monitor import *
from define import Define

print('bleno - echo')

bleno = Bleno()
monitor = Monitor(ssid_target=Define.SSID_TARGET)

SERVICE_UUID = Define.SERVICE_UUID
CHARACTERISTIC_UUID = Define.CHARACTERISTIC_UUID

characteristics = NFCCharacteristic(CHARACTERISTIC_UUID, monitor)
connected_device = []


def onStateChange(state):
    print('on -> stateChange: ' + state)

    if state == 'poweredOn':
        bleno.startAdvertising('nfcTrans', [SERVICE_UUID])
    else:
        bleno.stopAdvertising()


bleno.on('stateChange', onStateChange)


def onAdvertisingStart(error):
    print('on -> advertisingStart: ' + ('error ' + error if error else 'success'))

    if not error:
        bleno.setServices([
            BlenoPrimaryService({
                'uuid': SERVICE_UUID,
                'characteristics': [characteristics]
            })
        ])


def onDisconnected(clientAddress):
    connected_device.remove(clientAddress)
    if len(connected_device) == 0 and monitor.state.get("MONITORING"):
        monitor.stop()
    print("onDisconnected", connected_device)


def onAccept(clientAddress):
    connected_device.append(clientAddress)
    if len(connected_device) > 0 and not monitor.state.get("MONITORING"):
        monitor.start()
    print("Accepted", connected_device)


def nfcUpdate(tag):
    monitor_detected = monitor.state.pack()
    characteristics.Update(array.array('B', monitor_detected))


bleno.on('advertisingStart', onAdvertisingStart)
bleno.on('accept', onAccept)
bleno.on('disconnect', onDisconnected)

monitor.add_handler(nfcUpdate)

bleno.start()
# monitor.start()

print('Hit <ENTER> to disconnect')

input()

bleno.stopAdvertising()
bleno.disconnect()

print('terminated.')
sys.exit(1)
