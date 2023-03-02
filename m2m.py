# Start your engines
import minimalmodbus
import paho.mqtt.client as mqtt
import json
import time
 
# MQTT settings
MQTT_ADDRESS = 'localhost'
MQTT_PORT = 1883
MQTT_USERNAME = 'verycoolusername'
MQTT_PASSWORD = 'verycoolpassword'
 
# Modbus RTU settings
RS485_DEVICE = '/dev/ttyUSB0'
BAUDRATE = 9600
PARITY = 'N'
STOPBITS = 1
TIMEOUT = 1
SLAVE_ADDRESS = 1
 
# Sensors
DEVICE_NAME = 'GARO Power Meter'
IDENTIFIERS = 'GARO PM'
MANUFACTURER = 'GARO AB'
MODEL = 'GNM3T-LP RS485 N'
SENSORS = [
    {'address': 0, 'name': f'{DEVICE_NAME}-V_L1-N', 'unit_of_measurement': 'V', 'device_class': 'voltage', 'valweight': 10, 'round': 1, 'register_type': 'holding'},
    {'address': 2, 'name': f'{DEVICE_NAME}-V_L2-N', 'unit_of_measurement': 'V', 'device_class': 'voltage', 'valweight': 10, 'round': 1, 'register_type': 'holding'},
    {'address': 4, 'name': f'{DEVICE_NAME}-V_L3-N', 'unit_of_measurement': 'V', 'device_class': 'voltage', 'valweight': 10, 'round': 1, 'register_type': 'holding'},
    {'address': 6, 'name': f'{DEVICE_NAME}-V_L1-L2', 'unit_of_measurement': 'V', 'device_class': 'voltage', 'valweight': 10, 'round': 1, 'register_type': 'holding'},
    {'address': 8, 'name': f'{DEVICE_NAME}-V_L2-L3', 'unit_of_measurement': 'V', 'device_class': 'voltage', 'valweight': 10, 'round': 1, 'register_type': 'holding'},
    {'address': 10, 'name': f'{DEVICE_NAME}-V_L3-L1', 'unit_of_measurement': 'V', 'device_class': 'voltage', 'valweight': 10, 'round': 1, 'register_type': 'holding'},
    {'address': 12, 'name': f'{DEVICE_NAME}-A_L1', 'unit_of_measurement': 'A', 'device_class': 'current', 'valweight': 1000, 'round': 2, 'register_type': 'holding'},
    {'address': 14, 'name': f'{DEVICE_NAME}-A_L2', 'unit_of_measurement': 'A', 'device_class': 'current', 'valweight': 1000, 'round': 2, 'register_type': 'holding'},
    {'address': 16, 'name': f'{DEVICE_NAME}-A_L3', 'unit_of_measurement': 'A', 'device_class': 'current', 'valweight': 1000, 'round': 2, 'register_type': 'holding'},
    {'address': 40, 'name': f'{DEVICE_NAME}-kW_TOT', 'unit_of_measurement': 'kW', 'device_class': 'power', 'valweight': 10, 'round': 2, 'register_type': 'holding'},
    {'address': 51, 'name': f'{DEVICE_NAME}-Hz', 'unit_of_measurement': 'Hz', 'device_class': 'Frequency', 'valweight': 10, 'round': 1, 'register_type': 'holding'},
    {'address': 52, 'name': f'{DEVICE_NAME}-kWh_TOT', 'unit_of_measurement': 'kWh', 'device_class': 'energy', 'valweight': 10, 'round': 0, 'register_type': 'holding'},
    {'address': 90, 'name': f'{DEVICE_NAME}-run_hour_meter', 'unit_of_measurement': 'h', 'device_class': 'duration', 'valweight': 100, 'round': 0, 'register_type': 'holding'}
]
 
# Create modbus reader
instrument = minimalmodbus.Instrument(RS485_DEVICE, SLAVE_ADDRESS)
instrument.serial.baudrate = BAUDRATE
instrument.serial.parity = PARITY
instrument.serial.stopbits = STOPBITS
instrument.serial.timeout = TIMEOUT
 
# Create MQTT client
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_ADDRESS, MQTT_PORT)

# Publish MQTT message for every sensor
for sensor in SENSORS:
    message = {
        'name': sensor['name'],
        'unique_id': f"{sensor['name']}_sensor",
        'state_topic': f"homeassistant/sensor/{sensor['name']}/state",
        'unit_of_measurement': sensor['unit_of_measurement'],
        'device_class': sensor['device_class'],
        'value_template': '{{ value | float / ' + str(sensor["valweight"]) + ' | round(' + str(sensor["round"]) + ') }}',
        'device': {
            'name': DEVICE_NAME,
            'identifiers': [IDENTIFIERS],
            'manufacturer': MANUFACTURER,
            'model': MODEL
        }
    }
    client.publish(f"homeassistant/sensor/{sensor['name']}/config", json.dumps(message), retain=True)

# Get values from sensors and publish them to MQTT server, then repeat it forevah man
while True:
    for sensor in SENSORS:
        if sensor['register_type'] == 'holding':
            value = instrument.read_register(sensor['address'], 0, functioncode=3)
        elif sensor['register_type'] == 'input':
            value = instrument.read_register(sensor['address'], 0, functioncode=4)
        value = int(value) # convert to integer
        client.publish(f"homeassistant/sensor/{sensor['name']}/state", value)
    client.loop()
    time.sleep(5) # sshhh time to sleep for 5 seconds until next poll
