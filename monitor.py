import nfc
import threading
import subprocess
import time
from sched import scheduler

from _cffi_backend import typeof


class ID_State:
    def __init__(self) -> None:
        self._card_detected = False
        self._id_detected = False
        self._monitoring = False
        super().__init__()

    def set(self, key, val):
        if key == 'CARD_DETECTED':
            self._card_detected = val
            return True
        elif key == 'ID_DETECTED':
            self._id_detected = val
            return True
        elif key == 'MONITORING':
            self._monitoring = val
            return True
        return False

    def get(self, key):
        if key == 'CARD_DETECTED':
            return self._card_detected
        elif key == 'ID_DETECTED':
            return self._id_detected
        elif key == 'MONITORING':
            return self._monitoring
        return False

    def pack(self):
        int_array = [(self._id_detected << 2 | self._card_detected << 1 | self._monitoring)]
        return int_array


class Monitor:

    def __init__(self, ssid_target=None, scan_interval=1) -> None:
        super().__init__()
        self.nfc_thread = None
        self.scan_thread = None
        self.update_handler = []
        self.state = ID_State()
        self.scan_scheduler = None
        self.scan_scheduler_event = None
        if ssid_target is None:
            self.ssid_target = []
        else:
            self.ssid_target = ssid_target
        self.scan_interval = scan_interval

    def add_handler(self, handler):
        if handler is not None:
            self.update_handler.append(handler)

    def remove_handler(self, handler):
        if handler in self.update_handler:
            self.update_handler.remove(handler)

    def start(self):
        self.state.set('CARD_DETECTED', False)
        self.state.set('ID_DETECTED', False)
        self.state.set('MONITORING', True)
        try:
            self.clf = nfc.ContactlessFrontend('usb')
        except:
            return False
        self.nfc_thread = threading.Thread(target=self.run)
        self.nfc_thread.start()
        self.scan_scheduler = scheduler(time.time, time.sleep)
        self.scan_thread = threading.Thread(target=self.run_ssid_scan, args=(self.scan_interval, self.scan_scheduler,))
        self.scan_thread.start()
        # self.run_ssid_scan(self.scan_interval, self.scan_scheduler)
        pass
        return True

    def stop(self):
        self.state.set('CARD_DETECTED', False)
        self.state.set('ID_DETECTED', False)
        self.state.set('MONITORING', False)
        self.clf.close()
        self.scan_scheduler.cancel(self.scan_scheduler_event)
        return True

    def run(self):
        if self.clf:
            self.clf.connect(rdwr={
                'targets': ['106A'],
                'on-startup': self.startup,
                'on-connect': self.connected,
                'on-release': self.released,
            })

    def startup(self, targets):
        print("waiting for new NFC tags...")
        return targets

    def connected(self, tag):
        self.state.set('CARD_DETECTED', True)
        if tag.TYPE == 'Type4Tag' and tag.ndef is not None:
            if tag.ndef.records[0].uri == 'http://www.kddi.com/hr-nfc/':
                self.state.set('ID_DETECTED', True)
                print("id found.")
        # update hanlder呼び出し
        if len(self.update_handler) > 0:
            for handler in self.update_handler:
                handler(tag)

        return True

    def released(self, tag):
        self.state.set('CARD_DETECTED', False)
        self.state.set('ID_DETECTED', False)
        # update hanlder呼び出し
        if len(self.update_handler) > 0:
            for handler in self.update_handler:
                handler(tag)

        print("released:")

    def run_ssid_scan(self, interval, sc):
        if isinstance(sc, scheduler):
            self.scan_scheduler_event = sc.enter(interval, 1, self.scanSSID, (sc, interval))
            sc.run()
            print("thread_end")
            return True
        return False

    def scanSSID(self, sc, interval):
        stdout = subprocess.check_output("iwlist wlan0 scan | grep 'ESSID:\".\+\"'", shell=True)
        for line in stdout.split():
            ssid = line.decode().lstrip('ESSID:').strip('"')
            if ssid in self.ssid_target:
                print("ssid found", ssid)
        if isinstance(sc, scheduler):
            self.scan_scheduler_event = sc.enter(interval, 1, self.scanSSID, (sc, interval))
