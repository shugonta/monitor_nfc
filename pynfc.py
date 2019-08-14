import nfc
from nfc.clf import RemoteTarget
from pybleno import *


def startup(targets):
    print("waiting for new NFC tags...")
    return targets


def connected(tag):
    print("old message:")
    if tag.TYPE == 'Type4Tag' and tag.ndef is not None:
        if tag.ndef.records[0].uri == 'http://www.kddi.com/hr-nfc/':
            print(tag.ndef.records[0].uri)

    return True


def released(tag):
    print("released:")


clf = nfc.ContactlessFrontend('usb')
print(clf)
if clf:
    while clf.connect(rdwr={
        'targets': ['106A'],
        'on-startup': startup,
        'on-connect': connected,
        'on-release': released,
    }):
        pass
