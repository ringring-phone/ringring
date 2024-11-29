import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

import array
import gobject

mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'

class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'

class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'

class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'

class Advertisement(dbus.service.Object):
    PATH_BASE = '/com/ringring/phone/advertisement'

    def __init__(self, bus, index, name="CustomBLEDevice", advertising_type="peripheral"):
        self.path = f"{self.PATH_BASE}{index}"
        self.bus = bus
        self.ad_type = advertising_type
        self.local_name = name
        self.service_uuids = [WIFIService.WIFI_UUID]  # Include the UUID for your WiFiConfigService
        self.discoverable = True
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        properties = {
            "org.bluez.LEAdvertisement1": {
                "Type": self.ad_type,
                "LocalName": self.local_name,
                "Discoverable": self.discoverable,
                "Includes": ["tx-power"],
                "ServiceUUIDs": self.service_uuids
            }
        }
        return properties

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="ss", out_signature="v")
    def Get(self, interface, property):
        return self.get_properties()[interface][property]

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        return self.get_properties()[interface]

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="ssv")
    def Set(self, interface, property, value):
        pass

    @dbus.service.method("org.bluez.LEAdvertisement1", in_signature="")
    def Release(self):
        print(f"{self.path}: Released")

class GattService(dbus.service.Object):
    PATH_BASE = '/com/ringring/phone/service'

    def __init__(self, bus, index, uuid, primary=True):
        self.path = f"{self.PATH_BASE}{index}"
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)
        print(f"Registered GattService at {self.path}")  # Debug output

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                "UUID": self.uuid,
                "Primary": self.primary,
                "Characteristics": dbus.Array([c.get_path() for c in self.characteristics], signature="o")
            }
        }

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="ss", out_signature="v")
    def Get(self, interface, property):
        return self.get_properties()[interface][property]

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        return self.get_properties()[interface]
    
    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}

        response[self.get_path()] = self.get_properties()
        for chrc in self.characteristics:
            response[chrc.get_path()] = chrc.get_properties()
            descs = chrc.get_descriptors()
            for desc in descs:
                response[desc.get_path()] = desc.get_properties()

        return response

class GattCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = f"{service.get_path()}/char{index}"
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)
        print(f"Registered GattCharacteristic at {self.path}")  # Debug output

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, out_signature='ay')
    def ReadValue(self):
        print('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='ay')
    def WriteValue(self, value):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

class GattDescriptor(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = f"{characteristic.path}/desc{index}"
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE, out_signature='ay')
    def ReadValue(self):
        print ('Default ReadValue called, returning error')
        raise NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='ay')
    def WriteValue(self, value):
        print('Default WriteValue called, returning error')
        raise NotSupportedException()

def register_gatt_service(service):
    bus = dbus.SystemBus()
    adapter_path = "/org/bluez/hci0"
    gatt_manager = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.bluez.GattManager1")

    print("Registering GATT service...")
    try:
        gatt_manager.RegisterApplication(service.get_path(), {}, reply_handler=register_service_cb, error_handler=register_service_error_cb)
    except dbus.exceptions.DBusException as e:
        print(f"Exception during GATT service registration: {e}")

def register_ad_cb():
    print("Advertisement registered successfully.")

def register_ad_error_cb(error):
    print(f"Failed to register advertisement: {error}")
    mainloop.quit()

ad_manager = None
advertisement = None

def register_advertisement():
    bus = dbus.SystemBus()
    adapter_path = "/org/bluez/hci0"
    ad_manager = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.bluez.LEAdvertisingManager1")

    advertisement = Advertisement(bus, 0, name="RingRing Phone")
    ad_manager.RegisterAdvertisement(advertisement.get_path(), {}, reply_handler=register_ad_cb, error_handler=register_ad_error_cb)

    print("Starting advertisement...")

def unregister_advertisement():
    print("Stopping advertisement...")
    ad_manager.UnregisterAdvertisement(advertisement.get_path())
    

class WIFIService(GattService):
    WIFI_UUID = '12345678-1234-5678-1234-989898989898'

    def __init__(self, bus, index):
        GattService.__init__(self, bus, index, self.WIFI_UUID, True)
        self.add_characteristic(SSIDCharateristic(bus, 0, self))
        self.add_characteristic(PasswordCharateristic(bus, 1, self))

class SSIDCharateristic(GattCharacteristic):
    SSID_UUID = 'eeee5678-1234-5678-1234-989898989898'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.SSID_UUID,
                ['read', 'write'],
                service)
        self.value = "HankNet"

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="", out_signature="ay")
    def ReadValue(self, options):
        print('SSID ReadValue called, returning:', repr(self.value))
        # Convert the string to bytes and return as a byte array
        return dbus.Array(self.value.encode('utf-8'), signature='y')

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}", out_signature="")
    def WriteValue(self, value, options):
        # Convert the byte array to a string
        new_value = bytes(value).decode('utf-8')
        print('SSID WriteValue called with:', repr(new_value))
        self.value = new_value  # Update the value with the new string

class PasswordCharateristic(GattCharacteristic):
    PASSWORD_UUID = 'dddd5678-1234-5678-1234-989898989898'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.PASSWORD_UUID,
                ['write'],
                service)
        self.value = "password"

    def ReadValue(self):
        print('TestCharacteristic Read: ' + repr(self.value))
        return self.value

class TestService(GattService):
    """
    Dummy test service that provides characteristics and descriptors that
    exercise various API functionality.

    """
    TEST_SVC_UUID = '12345678-1234-5678-1234-989898989898'

    def __init__(self, bus, index):
        GattService.__init__(self, bus, index, self.TEST_SVC_UUID, True)
        self.add_characteristic(TestCharacteristic(bus, 0, self))
        self.add_characteristic(TestEncryptCharacteristic(bus, 1, self))

class TestCharacteristic(GattCharacteristic):
    """
    Dummy test characteristic. Allows writing arbitrary bytes to its value, and
    contains "extended properties", as well as a test descriptor.

    """
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef1'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = []
        self.add_descriptor(TestDescriptor(bus, 0, self))
        self.add_descriptor(
                CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self):
        print('TestCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value):
        print('TestCharacteristic Write: ' + repr(value))
        self.value = value


class TestDescriptor(GattDescriptor):
    """
    Dummy test descriptor. Returns a static value.

    """
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef2'

    def __init__(self, bus, index, characteristic):
        GattDescriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]

class TestEncryptCharacteristic(GattCharacteristic):
    """
    Dummy test characteristic requiring encryption.

    """
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef3'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['encrypt-read', 'encrypt-write'],
                service)
        self.value = []
        self.add_descriptor(TestEncryptDescriptor(bus, 2, self))
        self.add_descriptor(
                CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self):
        print('TestCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value):
        print('TestCharacteristic Write: ' + repr(value))
        self.value = value

class TestEncryptDescriptor(GattDescriptor):
    """
    Dummy test descriptor requiring encryption. Returns a static value.

    """
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef4'

    def __init__(self, bus, index, characteristic):
        GattDescriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['encrypt-read', 'encrypt-write'],
                characteristic)

    def ReadValue(self):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]

class CharacteristicUserDescriptionDescriptor(GattDescriptor):
    """
    Writable CUD descriptor.

    """
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        self.value = array.array('B', b'This is a characteristic for testing')
        self.value = self.value.tolist()
        GattDescriptor.__init__(
                self, bus, index,
                self.CUD_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self):
        return self.value

    def WriteValue(self, value):
        if not self.writable:
            raise NotPermittedException()
        self.value = value

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props:
            return o

    return None

def register_service_cb():
    print('GATT service registered')

def register_service_error_cb(error):
    print('Failed to register service: ' + str(error))
    mainloop.quit()

def device_connected_signal_handler(interface, changed_properties, invalidated_properties, path=None):
    print(f"device_connected_signal_handler {path}")
    print(f"changed_properties {changed_properties}")
    if path and 'Connected' in changed_properties:
        # Extract and format the MAC address from the path
        mac_address = path.split('/')[-1].replace('_', ':').upper()
        
        if changed_properties['Connected']:
            print(f"Device connected: {mac_address}")
        else:
            print(f"Device disconnected: {mac_address}")

# AGENT_INTERFACE = 'org.bluez.Agent1'
# CAPABILITY = 'NoInputNoOutput'

# class BluetoothAgent(dbus.service.Object):
#     def __init__(self, bus, path):
#         dbus.service.Object.__init__(self, bus, path)

#     @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
#     def Release(self):
#         print("Agent released")

#     @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
#     def RequestPinCode(self, device):
#         print("RequestPinCode called, responding with a dummy code")
#         return "0000"  # Return a fixed PIN code

#     @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
#     def RequestPasskey(self, device):
#         print("RequestPasskey called, responding with a dummy passkey")
#         return dbus.UInt32(123456)

#     @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
#     def DisplayPasskey(self, device, passkey):
#         print(f"DisplayPasskey ({device}): {passkey}")

#     @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
#     def RequestConfirmation(self, device):
#         print(f"RequestConfirmation for {device}, confirming automatically")
#         return  # Confirm automatically for "Just Works"

#     @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
#     def AuthorizeService(self, device, uuid):
#         print(f"AuthorizeService for {device}, UUID: {uuid}")
#         return  # Automatically authorize service

#     @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
#     def Cancel(self):
#         print("Agent request canceled")

# def register_agent(bus):
#     agent_path = "/test/agent"
#     agent = BluetoothAgent(bus, agent_path)
#     agent_manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"),
#                                    "org.bluez.AgentManager1")

#     agent_manager.RegisterAgent(agent_path, CAPABILITY)
#     print("Agent registered with capability:", CAPABILITY)

#     agent_manager.RequestDefaultAgent(agent_path)
#     print("Agent set as default")

def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    # test_service = TestService(bus, 0)
    wifi_service = WIFIService(bus, 0)

    # Set up a signal receiver to listen for interface property changes
    bus.add_signal_receiver(
        device_connected_signal_handler,
        dbus_interface="org.freedesktop.DBus.Properties",
        signal_name="PropertiesChanged",
        arg0="org.bluez.Device1",
        path_keyword='path'
    )

    # register_agent(bus)

    mainloop = GLib.MainLoop()

    try:
        service_manager.RegisterApplication(
            wifi_service.get_path(), {},
            reply_handler=register_service_cb,
            error_handler=register_service_error_cb
        )
        print("Service registration initiated.")

        register_advertisement()

        mainloop.run()
    except KeyboardInterrupt:
        unregister_advertisement()
        mainloop.quit()
    except Exception as e:
        print(f"Failed to start main loop: {e}")
        mainloop.quit()

if __name__ == "__main__":
    main()