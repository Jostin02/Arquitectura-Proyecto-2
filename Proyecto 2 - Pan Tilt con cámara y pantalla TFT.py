# ******* PROGRAMA PRINCIPAL *******
# ******* ARQUITECTURA DE COMPUTADORAS 1 *******
# ******* PROYECTO 2 - PAN TILT CON CÁMARA Y PANTALLA TFT *******

# Librerías generales
import time, board, busio, digitalio, struct, analogio

# Librería para el control de los servo motores
import pwmio

# Librerías para el control de la pantalla
import adafruit_ili9341
from displayio import (
    Bitmap,
    Group,
    TileGrid,
    FourWire,
    release_displays,
    ColorConverter,
    Colorspace,
)

# Librería para el control de la cámara
from adafruit_ov7670 import (
    OV7670,
    OV7670_SIZE_DIV1,
    OV7670_SIZE_DIV16,
)

""" Prueba realizada - optativa
pwm_servo_pan = pwmio.PWMOut(board.GP0, duty_cycle=2 ** 15, frequency=50)
servo_pan = servo.Servo(
    pwm_servo_pan, min_pulse=500, max_pulse=2200
)
desired_pan = 90
servo_pan.angle = desired_pan

pwm_servo_tilt = pwmio.PWMOut(board.GP1, duty_cycle=2 ** 15, frequency=50)
servo_tilt = servo.Servo(
    pwm_servo_tilt, min_pulse=500, max_pulse=2200
)
desired_tilt = 90
servo_tilt.angle = desired_tilt
"""
# Configuración de los servo motores
servo_pan = pwmio.PWMOut(board.GP0, duty_cycle=2 ** 15, frequency=50)
servo_tilt = pwmio.PWMOut(board.GP1, duty_cycle=2 ** 15, frequency=50)

# Configuración de los botones pulsadores o push buttoms de PAN
pan_mas = digitalio.DigitalInOut(board.GP16)
pan_mas.direction = digitalio.Direction.INPUT
pan_menos = digitalio.DigitalInOut(board.GP17)
pan_menos.direction = digitalio.Direction.INPUT

# Configuración de los botones pulsadores o push buttoms de TILT
tilt_mas = digitalio.DigitalInOut(board.GP18)
tilt_mas.direction = digitalio.Direction.INPUT
tilt_menos = digitalio.DigitalInOut(board.GP19)
tilt_menos.direction = digitalio.Direction.INPUT

# Valores iniciales de los servo motores 
valor_pan = 4586  # valor inicial
valor_tilt = 4586 # valor inicial

incremento = 364  # 10 grados - incremento por rotación

# Inicializa los servomotores
servo_pan.duty_cycle = 2 ** 15
servo_tilt.duty_cycle = 2 ** 15

# Ciclo de rotación de los servomotores
while True:
    if pan_mas.value == True:
        valor_pan = valor_pan + incremento
        if valor_pan > 7862:  # limite 180 grados
            valor_pan = 7862
        servo_pan.duty_u16(valor_pan)
        time.sleep(0.5)
    if pan_menos.value == True:
        valor_pan = valor_pan - incremento
        if valor_pan < 1311:  # limite 0 grados
            valor_pan = 1311
        servo_pan.duty_u16(valor_pan)
        time.sleep(0.5)
        
    if tilt_mas.value == True
        valor_tilt = valor_tilt + incremento
        if valor_tilt > 6406:  # limite 50 grados
            valor_tilt = 6406
        servo_tilt.duty_u16(valor_tilt)
        time.sleep(0.5)
    if tilt_menos.value == True:
        valor_tilt = valor_tilt - incremento
        if valor_tilt < 3130:  # limite 130 grados
            valor_tilt = 3130
        servo_tilt.duty_u16(valor_tilt)
        time.sleep(0.5)
    

# Configuración de la pantalla
displayio.release_displays()
spi = busio.SPI(clock=board.GP14, MOSI=board.GP15)
display_bus = displayio.FourWire(spi, command=board.GP20, chip_select=board.GP13, reset=board.GP12)
display = adafruit_ili9341(display_bus, width=320, height=240, rotation=270)

# Configuración de la cámara
# Inicialización de la cámara
with digitalio.DigitalInOut(board.GP28) as reset:
    reset.switch_to_output(False)
    time.sleep(0.001)
    bus = busio.I2C(board.GP3, board.GP2)

# Orden de conexiones de los pines de la cámara
cam = OV7670(
    bus,
    data_pins=[
        board.GP4,
        board.GP5,
        board.GP6,
        board.GP7,
        board.GP8,
        board.GP9,
        board.GP10,
        board.GP11,
    ], 
    clock=board.GP26,  # [xlk]
    vsync=board.GP21,  # [vs]
    href=board.GP27,  # [hs] 
    mclk=board.GP22,  # [plk]
    shutdown=None,
    reset=board.GP28, # [reset]
)

width = display.width
height = display.height

# cam.test_pattern = OV7670_TEST_PATTERN_COLOR_BAR

bitmap = None

# Selección del tamaño más grande para el cual podemos asignar un mapa de bits con éxito y que no es más grande que la pantalla
for size in range(OV7670_SIZE_DIV1, OV7670_SIZE_DIV16 + 1):
    cam.size = size
    if cam.width > width:
        continue
    if cam.height > height:
        continue
    try:
        bitmap = Bitmap(cam.width, cam.height, 65536)
        break
    except MemoryError:
        continue

print(width, height, cam.width, cam.height)
if bitmap is None:
    raise SystemExit("Could not allocate a bitmap")

g = displayio.Group(scale=1, x=(width - cam.width) // 2, y=(height - cam.height) // 2)
tg = displayio.TileGrid(
    bitmap, pixel_shader=displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565_SWAPPED)
)
g.append(tg)
display.root_group = g

t0 = time.monotonic_ns()
display.auto_refresh = False
while True:
    cam.capture(bitmap)
    bitmap.dirty()
    display.refresh(minimum_frames_per_second=0)
    t1 = time.monotonic_ns()
    print("fps", 1e9 / (t1 - t0))
    t0 = t1
