import nfc
import threading
import struct
import subprocess


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

    def __init__(self, ssid_target=None) -> None:
        super().__init__()
        self.thread = None
        self.thread_end = False
        self.update_handler = []
        self.state = ID_State()
        if ssid_target is None:
            self.ssid_target = []
        else:
            self.ssid_target = ssid_target
        self.scanSSID()

    def add_handler(self, handler):
        if handler is not None:
            self.update_handler.append(handler)

    def remove_handler(self, handler):
        if handler in self.update_handler:
            self.update_handler.remove(handler)

    def start(self):
        self.thread_end = False
        self.state.set('CARD_DETECTED', False)
        self.state.set('ID_DETECTED', False)
        self.state.set('MONITORING', True)
        try:
            self.clf = nfc.ContactlessFrontend('usb')
        except:
            return False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        return True

    def stop(self):
        self.state.set('CARD_DETECTED', False)
        self.state.set('ID_DETECTED', False)
        self.state.set('MONITORING', False)
        self.clf.close()
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

    def scanSSID(self):
        stdout = subprocess.check_output("iwlist wlan0 scan | grep 'ESSID:\".\+\"'", shell=True)
        for line in stdout.split():
            ssid = line.decode().lstrip('ESSID:').strip('"')
            if ssid in self.ssid_target:
                print("ssid found", ssid)
                pass
