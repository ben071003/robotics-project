# ble_uart.py - Bluetooth Low Energy "UART" (Nordic UART service)
import bluetooth
import time

_UART_SERVICE = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_NOTIFY)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE,
)


class BLEUart:
    def __init__(self, name):
        self.name = name
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)
        ((self.tx, self.rx),) = self.ble.gatts_register_services(
            ((_UART_SERVICE, (_UART_TX, _UART_RX)),)
        )
        self.conns = set()
        self.buf = b""
        self._advertise()

    def _advertise(self):
        n = self.name.encode()
        adv = bytes([2, 0x01, 0x06]) + bytes([len(n) + 1, 0x09]) + n
        self.ble.gap_advertise(100000, adv_data=adv)

    def _irq(self, event, data):
        if event == 1:      # connected
            self.conns.add(data[0])
        elif event == 2:    # disconnected
            self.conns.discard(data[0])
            self._advertise()
        elif event == 3:    # data written by the phone
            _, handle = data
            if handle == self.rx:
                self.buf += self.ble.gatts_read(self.rx)

    def read(self):
        data, self.buf = self.buf, b""
        return data

    def send(self, text):
        """Send text to the phone in 20-byte chunks (default BLE limit)."""
        data = text.encode()
        for c in list(self.conns):
            for i in range(0, len(data), 20):
                try:
                    self.ble.gatts_notify(c, self.tx, data[i:i + 20])
                except OSError:
                    pass
                time.sleep_ms(10)
