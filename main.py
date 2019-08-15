from pybleno import *
import sys
import signal
from NFCCharacteristic import *
from monitor import *

print('bleno - echo')

bleno = Bleno()
monitor = Monitor()

SERVICE_UUID = '54c3259f-a142-4711-bbca-2efba019868e'
CHARACTERISTIC_UUID = '5170e77f-4076-40b7-9a87-15fbe60e816d'

characteristics = NFCCharacteristic(CHARACTERISTIC_UUID, monitor)


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


def nfcUpdate(tag):
    monitor_detected = (monitor.CARD_DETECTED | monitor.ID_DETECTED << 1)
    characteristics.Update(array.array('B', [monitor_detected]))


bleno.on('advertisingStart', onAdvertisingStart)

monitor.add_handler(nfcUpdate)

bleno.start()
monitor.start()

print('Hit <ENTER> to disconnect')

if (sys.version_info > (3, 0)):
    input()

bleno.stopAdvertising()
bleno.disconnect()

print('terminated.')
sys.exit(1)
