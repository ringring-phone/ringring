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

mainloop = None

class Advertisement(dbus.service.Object):
    PATH_BASE = "/org/bluez/example/advertisement"

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.manufacturer_data = None
        self.local_name = None
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = dict()
        properties["Type"] = self.ad_type
        if self.local_name is not None:
            properties["LocalName"] = dbus.String(self.local_name)
        if self.manufacturer_data is not None:
            properties["ManufacturerData"] = dbus.Dictionary(self.manufacturer_data, signature='qv')
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dict()
        self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

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

class SimpleNamediBeacon(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "broadcast")
        
        # Set the visible name
        self.add_local_name("MyBeacon")
        
        # Add iBeacon data
        # AirLocate UUID
        uuid_bytes = [
            0x55, 0x4B, 0xCF, 0xCE,
            0x17, 0x4E, 0x4B, 0xAC,
            0xA8, 0x14, 0x09, 0x2E,
            0x77, 0xF6, 0xB7, 0xE5
        ]
        
        # Standard iBeacon prefix
        prefix = [0x02, 0x15]
        
        # Major and Minor versions
        major = [0x00, 0x01]  # Major version 1
        minor = [0x00, 0x01]  # Minor version 1
        
        # Calibrated TX Power at 1 meter
        power = [0xC7]  # -57 dB
        
        # Combine all fields
        manufacturer_data = prefix + uuid_bytes + major + minor + power
        
        # Add manufacturer data (Apple's company identifier: 0x004C)
        self.add_manufacturer_data(0x004C, manufacturer_data)

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if LE_ADVERTISING_MANAGER_IFACE in props:
            return o
    return None

def register_ad_cb():
    print("Advertisement registered successfully")
    print("Broadcasting as 'MyBeacon'")
    print("UUID: 554BCFCE-174E-4BAC-A814-092E77F6B7E5")
    print("Major: 1, Minor: 1")

def register_ad_error_cb(error):
    print(f"Failed to register advertisement: {error}")
    mainloop.quit()

def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print("LEAdvertisingManager1 interface not found")
        return

    adapter_props = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        "org.freedesktop.DBus.Properties"
    )

    # Reset the adapter
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(0))
    time.sleep(1)
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))
    time.sleep(1)

    ad_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        LE_ADVERTISING_MANAGER_IFACE
    )

    advertisement = SimpleNamediBeacon(bus, 0)
    mainloop = GLib.MainLoop()

    try:
        ad_manager.RegisterAdvertisement(
            advertisement.get_path(),
            {},
            reply_handler=register_ad_cb,
            error_handler=register_ad_error_cb
        )
        print("Starting advertisement...")
        mainloop.run()
    except KeyboardInterrupt:
        print("\nAdvertisement stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        try:
            ad_manager.UnregisterAdvertisement(advertisement.get_path())
            print("Advertisement unregistered")
        except Exception as e:
            print(f"Error unregistering advertisement: {e}")

if __name__ == "__main__":
    main()