import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, name="CustomBLEDevice", advertising_type="peripheral"):
        self.path = f"{self.PATH_BASE}{index}"
        self.bus = bus
        self.ad_type = advertising_type
        self.local_name = name
        self.service_uuids = ["c165c1f5-88a4-46a5-a363-11111111db22"]
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

def register_advertisement():
    bus = dbus.SystemBus()
    adapter_path = "/org/bluez/hci0"
    ad_manager = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.bluez.LEAdvertisingManager1")

    advertisement = Advertisement(bus, 0, name="RingRing Phone")
    ad_manager.RegisterAdvertisement(advertisement.get_path(), {}, reply_handler=register_ad_cb, error_handler=register_ad_error_cb)

    global mainloop
    mainloop = GLib.MainLoop()
    try:
        print("Starting advertisement...")
        mainloop.run()
    except KeyboardInterrupt:
        print("Stopping advertisement...")
        ad_manager.UnregisterAdvertisement(advertisement.get_path())
        mainloop.quit()

def register_ad_cb():
    print("Advertisement registered successfully!")

def register_ad_error_cb(error):
    print(f"Failed to register advertisement: {error}")
    mainloop.quit()

if __name__ == "__main__":
    register_advertisement()