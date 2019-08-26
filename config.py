import configparser


class Config:
    def __init__(self, configfile) -> None:
        self.configfile = configfile
        self.config = configparser.ConfigParser()
        self.config.read(configfile)
        self._onchangecallback = None

    def setChangeHandler(self, handler):
        self._onchangecallback = handler

    def getSSIDList(self):
        if self.config is not None:
            if 'SSID' in self.config and 'target_ssid' in self.config['SSID']:
                target_ssid = self.config['SSID']['target_ssid']
                if target_ssid == "":
                    return []
                else:
                    return target_ssid.split(',')
            else:
                return []

    def setSSIDList(self, target_ssid_list):
        if self.config is not None:
            if 'SSID' in self.config:
                if 'target_ssid' in self.config['SSID']:
                    target_ssids = ','.join(target_ssid_list)
                    self.config.set('SSID', 'target_ssid', target_ssids)
                else:
                    target_ssids = ','.join(target_ssid_list)
                    self.config.set('SSID', 'target_ssid', ("%s", target_ssids))
            else:
                self.config.add_section('SSID')
                target_ssids = ','.join(target_ssid_list)
                self.config.set('SSID', 'target_ssid', ("%s", target_ssids))

        with open(self.configfile, 'w') as file:
            self.config.write(file)

        if self._onchangecallback is not None:
            self._onchangecallback(target_ssid_list)

    def addSSIDList(self, target_ssid):
        target_ssid_list = []
        if self.config is not None:
            if 'SSID' in self.config:
                if 'target_ssid' in self.config['SSID']:
                    target_ssid_list = self.getSSIDList()
                    if target_ssid not in target_ssid_list:
                        target_ssid_list.append(target_ssid)
                    target_ssids = ','.join(target_ssid_list)
                    self.config.set('SSID', 'target_ssid', target_ssids)

                else:
                    self.config.set('SSID', 'target_ssid', ("%s", target_ssid))
                    target_ssid_list.append(target_ssid)
            else:
                self.config.add_section('SSID')
                self.config.set('SSID', 'target_ssid', ("%s", target_ssid))
                target_ssid_list.append(target_ssid)

        with open(self.configfile, 'w') as file:
            self.config.write(file)

        if self._onchangecallback is not None:
            self._onchangecallback(target_ssid_list)

    def removeSSIDList(self, target_ssid):
        target_ssid_list = []
        if self.config is not None:
            if 'SSID' in self.config:
                if 'target_ssid' in self.config['SSID']:
                    target_ssid_list = self.getSSIDList()
                    if target_ssid in target_ssid_list:
                        target_ssid_list.remove(target_ssid)
                    target_ssids = ','.join(target_ssid_list)
                    self.config.set('SSID', 'target_ssid', target_ssids)

        with open(self.configfile, 'w') as file:
            self.config.write(file)

        if self._onchangecallback is not None:
            self._onchangecallback(target_ssid_list)
