#!/usr/bin/env python
# encoding: utf-8
"""
hal_smartplug.py

TP-Link HS110 HAL driver

Copyright Alexander Rössler <mail AT roessler DOT systems>
"""

import time
import argparse
import socket
import json

import hal


class HS110():
    def __init__(self, ip):
        self.ip = ip
        self.port = 9999  # standard port
        self.connected = False
        self.timeout = 0.25
        self.socket = None
        self.recv_buffer = 2048
        # status
        self.enable = False
        self.voltage = 0.0
        self.current = 0.0
        self.power = 0.0
        self.energy = 0.0
        self.error = False

    # source: https://github.com/softScheck/tplink-smartplug
    # Encryption and Decryption of TP-Link Smart Home Protocol
    # XOR Autokey Cipher with starting key = 171
    def encrypt(self, string):
        key = 171
        result = "\0\0\0\0"
        for i in string:
            a = key ^ ord(i)
            key = a
            result += chr(a)
        return result

    def decrypt(self, string):
        key = 171
        result = ""
        for i in string:
            a = key ^ ord(i)
            key = ord(i)
            result += chr(a)
        return result

    def connectSocket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        try:
            self.socket.connect((self.ip, self.port))
            self.connected = True
        except socket.error:
            self.socket = None

    def closeSocket(self):
        if self.socket is not None:
            try:
                self.socket.close()
            finally:
                self.socket = None
        self.connected = False

    def socketCmd(self, cmd):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.ip, self.port))
            sock.send(self.encrypt(cmd))
            data = sock.recv(self.recv_buffer)
            sock.close()
            data = self.decrypt(data[4:])
            return json.loads(data)
        except socket.error:
            self.handleError()
            return None

    def handleError(self):
        self.error = True

    def update(self):
        self.error = False
        self.updateStatus()

    def updateStatus(self):
        cmd = '{"emeter":{"get_realtime":{}},' + \
              '"system":{"get_sysinfo":null}}'

        data = self.socketCmd(cmd)
        if data is None:
            return
        sysinfo = data['system']['get_sysinfo']
        err_code = sysinfo['err_code']
        if not err_code:
            self.enable = sysinfo['relay_state']
        else:
            self.handleError()
        realtime = data['emeter']['get_realtime']
        err_code = realtime['err_code']
        if not err_code:
            self.current = realtime['current']
            self.voltage = realtime['voltage']
            self.power = realtime['power']
            self.energy = realtime['total']
        else:
            self.handleError()

    def setRelayState(self, state):
        cmd = '{"system":{"set_relay_state":{"state":%i}}}' % int(state)
        data = self.socketCmd(cmd)
        if data is None:
            return
        result = data['system']['set_relay_state']
        err_code = result['err_code']
        if not err_code:
            self.enabled = state
        else:
            self.handleError()


def main():
    # Check if IP is valid
    def validIP(ip):
        try:
            socket.inet_pton(socket.AF_INET, ip)
        except socket.error:
            parser.error("Invalid IP Address.")
        return ip

    parser = argparse.ArgumentParser(description='HAL component to read Temperature values over I2C')
    parser.add_argument('-n', '--name', help='HAL component name', required=True)
    parser.add_argument('-i', '--interval', help='Value update interval', default=0.5)
    parser.add_argument('-t', '--timeout', help='Allowed network delay before timeout', default=0.5)
    parser.add_argument('-a', '--address', metavar='<ip>',
                        required=True, help='Target IP Address', type=validIP)

    args = parser.parse_args()

    updateInterval = float(args.interval)
    timeout = float(args.timeout)
    address = args.address

    h = hal.component(args.name)
    enablePin = h.newpin('enable', hal.HAL_BIT, hal.HAL_IO)
    currentPin = h.newpin('current', hal.HAL_FLOAT, hal.HAL_OUT)
    voltagePin = h.newpin('voltage', hal.HAL_FLOAT, hal.HAL_OUT)
    powerPin = h.newpin('power', hal.HAL_FLOAT, hal.HAL_OUT)
    energyPin = h.newpin('energy', hal.HAL_FLOAT, hal.HAL_OUT)
    errorPin = h.newpin('error', hal.HAL_BIT, hal.HAL_OUT)
    h.ready()

    last_hal_enable = False
    last_plug_enable = False
    plug = HS110(address)
    plug.timeout = timeout

    try:
        while (True):
            startTime = time.time()

            # update device status
            plug.update()
            # update may return an error
            if not plug.error:
                currentPin.value = plug.current
                voltagePin.value = plug.voltage
                powerPin.value = plug.power
                energyPin.value = plug.energy
                enable = enablePin.value
                # update relay state
                if last_hal_enable != enable and enable != plug.enable:
                    plug.setRelayState(enable)
                    if not plug.error:
                        last_hal_enable = enable
                elif last_plug_enable != plug.enable:
                    last_hal_enable = plug.enable
                    enablePin.value = plug.enable
                    last_plug_enable = plug.enable
            errorPin.value = plug.error

            sleepTime = updateInterval - (time.time() - startTime)  # corrects for processing time
            time.sleep(max(sleepTime, 0.0))

    except KeyboardInterrupt:
        print(("exiting HAL component " + args.name))
        h.exit()

if __name__ == "__main__":
    main()
