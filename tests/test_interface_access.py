from pydbus import SystemBus

bus = SystemBus()
adapter = bus.get("org.bluez", "/org/bluez/hci0")

print("Introspecting /org/bluez/hci0:")
print(adapter.Introspect())