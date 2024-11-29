#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
import dbus.service
import time
import threading

try:
    from gi.repository import GLib
except ImportError:
    from gi.repository import GObject as GLib

BLUEZ_SERVICE_NAME = "org.bluez"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"

mainloop = None

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = "/"
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()

        return response

class Advertisement(dbus.service.Object):
    PATH_BASE = "/org/bluez/example/advertisement"

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.local_name = None
        self.include_tx_power = True
        self.flags = ["general-discoverable", "le-only"]
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties["Type"] = self.ad_type
        if self.service_uuids is not None:
            properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature='s')
        if self.local_name is not None:
            properties["LocalName"] = dbus.String(self.local_name)
        if self.include_tx_power:
            properties["Includes"] = dbus.Array(["tx-power"], signature='s')
        if self.flags:
            properties["Flags"] = dbus.Array(self.flags, signature='s')
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_local_name(self, name):
        self.local_name = dbus.String(name)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException(
                "org.bluez.Error.InvalidArguments",
                "Invalid interface")
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature='', out_signature='')
    def Release(self):
        print(f"{self.path}: Released!")

class Service(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                        in_signature='s',
                        out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise dbus.exceptions.DBusException(
                "org.bluez.Error.InvalidArguments",
                "Invalid interface")
        return self.get_properties()[GATT_SERVICE_IFACE]

class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.value = [0]
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                'Service': self.service.get_path(),
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
        if interface != GATT_CHRC_IFACE:
            raise dbus.exceptions.DBusException(
                "org.bluez.Error.InvalidArguments",
                "Invalid interface")
        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='', out_signature='ay')
    def ReadValue(self, options=None):
        print('ReadValue: ' + str(self.value))
        return self.value

class DeviceInfoService(Service):
    DEVICE_INFO_UUID = '180A'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.DEVICE_INFO_UUID, True)
        self.add_characteristic(ModelNameCharacteristic(bus, 0, self))

class ModelNameCharacteristic(Characteristic):
    MODEL_NAME_UUID = '2A24'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.MODEL_NAME_UUID,
            ['read'],
            service)
        self.value = bytes("Test Device", "utf-8")

def register_app_cb():
    print('GATT application registered')

def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()

def register_ad_cb():
    print('Advertisement registered')

def register_ad_error_cb(error):
    print('Failed to register advertisement: ' + str(error))
    mainloop.quit()

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                              DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None

def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)

    if not adapter:
        print('GattManager1 interface not found')
        return

    adapter_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                 "org.freedesktop.DBus.Properties")
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))
    adapter_props.Set("org.bluez.Adapter1", "Alias", "RingRing Phone 0001")

    # Create GATT Application
    app = Application(bus)
    device_info_service = DeviceInfoService(bus, 0)
    app.add_service(device_info_service)

    # Register GATT Application
    service_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        GATT_MANAGER_IFACE)
    
    service_manager.RegisterApplication(app.get_path(), {},
                                     reply_handler=register_app_cb,
                                     error_handler=register_app_error_cb)

    # Create and register advertisement
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                               LE_ADVERTISING_MANAGER_IFACE)
    
    advertisement = Advertisement(bus, 0, 'peripheral')
    advertisement.add_service_uuid(DeviceInfoService.DEVICE_INFO_UUID)
    advertisement.add_local_name("iOSTest")

    ad_manager.RegisterAdvertisement(advertisement.get_path(), {},
                                   reply_handler=register_ad_cb,
                                   error_handler=register_ad_error_cb)

    mainloop = GLib.MainLoop()
    
    print('Starting service. Press Ctrl+C to exit.')
    
    try:
        mainloop.run()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        ad_manager.UnregisterAdvertisement(advertisement.get_path())
        print('Advertisement unregistered')
        dbus.service.Object.remove_from_connection(advertisement)
        
if __name__ == '__main__':
    main()