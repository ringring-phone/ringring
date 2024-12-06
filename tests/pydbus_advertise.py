from pydbus import SystemBus
from gi.repository import GLib

class Advertisement:
    """
    Class to represent a BLE advertisement.
    """
    dbus = "org.bluez.LEAdvertisement1"

    def __init__(self, bus, index, name="TestBLE"):
        self.path = f"/org/bluez/example/advertisement{index}"
        self.ad_type = "peripheral"
        self.local_name = name
        self.service_uuids = ["12345678-1234-5678-1234-56789abcdef0"]

    def get_path(self):
        return self.path

    def get_properties(self):
        return {
            'org.bluez.LEAdvertisement1': {
                'Type': self.ad_type,
                'LocalName': self.local_name,
                'ServiceUUIDs': self.service_uuids
            }
        }

    def Release(self):
        print(f"{self.path}: Released")

def main():
    bus = SystemBus()
    ad_manager = bus.get('org.bluez', '/org/bluez/hci0')['org.bluez.LEAdvertisingManager1']

    # Create an instance of the advertisement
    advertisement = Advertisement(bus, 0, name="TestBLE")

    try:
        # Register the advertisement object with bluez
        ad_manager.RegisterAdvertisement(advertisement.get_path(), {})
        print("Advertisement registered successfully!")

        loop = GLib.MainLoop()
        print("Starting main loop for advertisement...")
        loop.run()

    except Exception as e:
        print(f"Failed to register advertisement: {e}")

if __name__ == "__main__":
    main()