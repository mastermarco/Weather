class Wifiprofile:
    ssid = ""
    auth = ""
    akm = ""
    cipher = ""
    key = ""

    def __init__(self, ssid, auth, akm, cipher):
        #print(ssid, auth, akm, cipher)
        self.ssid = ssid
        self.auth = auth
        self.akm = akm
        self.cipher = cipher
        '''if auth == 0:
            self.auth = 'open'
        else:
            self.auth = 'shared'

        if akm == 0:
            self.akm = 'NONE'
        elif akm == 1:
            self.akm = 'WPA'
        elif akm == 2:
            self.akm = 'WPAPSK'
        elif akm == 3:
            self.akm = 'WPA2'
        elif akm == 4:
            self.akm = 'WPA2PSK'
        elif akm == 5:
            self.akm = 'OTHER'

        if cipher == 0:
            self.cipher = 'NONE'
        elif cipher == 1:
            self.cipher = 'WEP'
        elif cipher == 2:
            self.cipher = 'TKIP'
        elif cipher == 3:
            self.cipher = 'AES'
        elif cipher == 4:
            self.cipher = 'UNKNOWN'
        '''
