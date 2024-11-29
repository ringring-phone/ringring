from pydbus import SystemBus

bus = SystemBus()
bluez_service = bus.get('org.bluez', '/')

try:
    # Access ObjectManager from org.bluez service
    om = bluez_service['org.freedesktop.DBus.ObjectManager']
    managed_objects = om.GetManagedObjects()

    for path, interfaces in managed_objects.items():
        print(f"Path: {path}")
        for iface in interfaces:
            print(f"  Interface: {iface}")

except Exception as e:
    print(f"Error: {e}")