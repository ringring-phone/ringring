from pydbus import SystemBus
from gi.repository import GLib, GObject
from dbus.mainloop.glib import DBusGMainLoop

# Initialize the main loop for D-Bus
DBusGMainLoop(set_as_default=True)
bus = SystemBus()

SERVICE_PATH = '/com/example/service0'
CHARACTERISTIC_PATH = '/com/example/service0/char0'
SERVICE_IFACE = 'org.bluez.GattService1'
CHARACTERISTIC_IFACE = 'org.bluez.GattCharacteristic1'

class GattService(GObject.GObject):
    """
    GATT Service class implementing the org.bluez.GattService1 interface.
    """
    def __init__(self, service_uuid, primary=True):
        super().__init__()
        self.service_uuid = service_uuid
        self.primary = primary
        self.characteristics = []

    def get_properties(self):
        return {
            'UUID': self.service_uuid,
            'Primary': self.primary,
            'Characteristics': self.characteristics,
        }

class GattCharacteristic(GObject.GObject):
    """
    GATT Characteristic class implementing the org.bluez.GattCharacteristic1 interface.
    """
    def __init__(self, char_uuid, service_path, flags):
        super().__init__()
        self.char_uuid = char_uuid
        self.service_path = service_path
        self.flags = flags
        self.value = [0x00]

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        self.value = value
        print(f"Characteristic value updated to: {self.value}")

    def get_properties(self):
        return {
            'UUID': self.char_uuid,
            'Service': self.service_path,
            'Flags': self.flags,
        }

# Create and register the service and characteristic objects
service = GattService(service_uuid='12345678-1234-5678-1234-56789abcdef0')
characteristic = GattCharacteristic(
    char_uuid='12345678-1234-5678-1234-56789abcdef1',
    service_path=SERVICE_PATH,
    flags=['read', 'write']
)

# Link the characteristic to the service
service.characteristics.append(CHARACTERISTIC_PATH)

# Register the service with BlueZ using the adapter interface
adapter = bus.get('org.bluez', '/org/bluez/hci0')
adapter.RegisterApplication(SERVICE_PATH, {})

print("GATT service and characteristic registered with BlueZ")
GLib.MainLoop().run()