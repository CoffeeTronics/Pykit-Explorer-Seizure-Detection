import board
import neopixel
from adafruit_icm20x import ICM20649
from API.i2c_bus import I2CBus
from API.lcd_display import LCDDisplay
from API.ble_uart import BLEUart
from API.audio_out import AudioOutput
from config import NUM_PIXELS


def init_hardware():
    pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_PIXELS, brightness=0.3, auto_write=False)

    i2c = I2CBus()
    imu = ICM20649(i2c.bus, 0x69)

    lcd = LCDDisplay()
    lcd.backlight_on()

    try:
        audio = AudioOutput()
    except Exception:
        audio = None

    try:
        ble = BLEUart()
    except Exception:
        ble = None

    return pixels, imu, lcd, audio, ble