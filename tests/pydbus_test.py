from pydbus import SystemBus

bus = SystemBus()
try:
    # Access the adapter interface
    adapter = bus.get("org.bluez", "/org/bluez/hci0")
    print("Adapter accessed successfully")

    # Access the LEAdvertisingManager interface
    ad_manager = bus.get("org.bluez", "/org/bluez/hci0")["org.bluez.LEAdvertisingManager1"]
    print("Advertising Manager accessed successfully")

except Exception as e:
    print(f"Error: {e}")