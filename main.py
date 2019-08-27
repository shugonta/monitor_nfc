from pybleno import *
import sys
import signal
from MonitorCharacteristic import *
from SSIDCharacteristic import *
from monitor import *
from define import Define
from config import Config

print('bleno - echo')


def onSSIDConfigChange(target_ssid_list):
    monitor.ssid_target = target_ssid_list


bleno = Bleno()
config = Config(Define.CONFIG_FILE)
config.setChangeHandler(onSSIDConfigChange)
ssid_target = config.getSSIDList()

monitor = Monitor(ssid_target=ssid_target, scan_interval=Define.SSID_SCAN_INTERVAL)

SERVICE_UUID = Define.SERVICE_UUID
CHARACTERISTIC_UUID = Define.CHARACTERISTIC_UUID
SSID_CHARACTERISTIC_UUID = Define.SSID_CHARACTERISTIC_UUID

characteristics = MonitorCharacteristic(CHARACTERISTIC_UUID, monitor)
ssid_characteristics = SSIDCharacteristic(SSID_CHARACTERISTIC_UUID, config)
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
                'characteristics': [characteristics, ssid_characteristics]
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

while True:
    try:
            time.sleep(1)
    except KeyboardInterrupt:
        bleno.stopAdvertising()
        bleno.disconnect()

        print('terminated.')
        sys.exit(1)

