import nfc
import threading


class Monitor:
    CARD_DETECTED = False
    ID_DETECTED = False

    clf = None
    thread = None
    update_handler = []

    def __init__(self) -> None:
        super().__init__()
        self.clf = nfc.ContactlessFrontend('usb')

    def add_handler(self, handler):
        if handler is not None:
            self.update_handler.append(handler)

    def remove_handler(self, handler):
        if handler in self.update_handler:
            self.update_handler.remove(handler)

    def start(self):
        self.thread = threading.Thread(target=self.run())

    def run(self):
        if self.clf:
            while self.clf.connect(rdwr={
                'targets': ['106A'],
                'on-startup': self.startup,
                'on-connect': self.connected,
                'on-release': self.released,
            }):
                pass

    def startup(self, targets):
        print("waiting for new NFC tags...")
        return targets

    def connected(self, tag):
        self.CARD_DETECTED = True
        if tag.TYPE == 'Type4Tag' and tag.ndef is not None:
            if tag.ndef.records[0].uri == 'http://www.kddi.com/hr-nfc/':
                self.ID_DETECTED = True
                print(tag.ndef.records[0].uri)
        # update hanlder呼び出し
        if len(self.update_handler) > 0:
            for handler in self.update_handler:
                handler(tag)

        return True

    def released(self, tag):
        self.CARD_DETECTED = False
        self.ID_DETECTED = False
        # update hanlder呼び出し
        if len(self.update_handler) > 0:
            for handler in self.update_handler:
                handler(tag)

        print("released:")
