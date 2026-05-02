from API.lcd_display import Colors as LCDColors
from config import CLASS_SEIZURE, CLASS_FALL, CLASS_STATIONARY


class OutputManager:

    def __init__(self, lcd, audio, ble):
        self._lcd   = lcd
        self._audio = audio
        self._ble   = ble

        self._last_lcd_class   = None
        self._last_audio_class = None

        self._lcd_group, self._lcd_palette = lcd.make_group(LCDColors.DARK_BLUE)
        self._header_lbl = lcd.add_label(
            self._lcd_group, "PyKit Explorer", 120, 8,
            color=LCDColors.WHITE, scale=2,
        )
        self._status_lbl = lcd.add_label(
            self._lcd_group, CLASS_STATIONARY, 120, 60,
            color=LCDColors.GREEN, scale=3,
        )

    def poll_ble(self):
        if self._ble is not None:
            self._ble.poll()

    def update_lcd(self, activity_class):
        if activity_class == self._last_lcd_class:
            return
        self._last_lcd_class  = activity_class
        self._status_lbl.color = (
            LCDColors.RED
            if activity_class in (CLASS_SEIZURE, CLASS_FALL)
            else LCDColors.GREEN
        )
        self._status_lbl.text = activity_class

    def update_audio(self, activity_class):
        if self._audio is None or activity_class == self._last_audio_class:
            return
        self._last_audio_class = activity_class
        if activity_class == CLASS_SEIZURE:
            if not self._audio.is_playing:
                self._audio.play_wav("AudioFiles/smb_stomp.wav", loop=True)
        else:
            self._audio.stop()

    def send_ble_alert(self, activity_class):
        if self._ble is None or not self._ble.connected:
            return
        try:
            self._ble.send("ALERT:" + activity_class + "\r\n")
            print("[BLE] Sent alert: ALERT:" + activity_class)
        except Exception as e:
            print("[BLE] Send failed:", e)