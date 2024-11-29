#!/usr/bin/env python3
import os
import json
import dbus
import dbus.mainloop.glib
import dbus.service
import socket
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

class WifiService(Service):
    WIFI_UUID = '00001111-e78c-7da4-b183-1b46ca5541a9'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.WIFI_UUID, True)
        self.ssid_char = SSIDCharacteristic(bus, 0, self)
        self.password_char = PasswordCharacteristic(bus, 1, self)
        self.address_char = AddressCharacteristic(bus, 2, self)
        self.add_characteristic(self.ssid_char)
        self.add_characteristic(self.password_char)
        self.add_characteristic(self.address_char)
        self.tcp_thread = None
        self.tcp_running = False

    def start_tcp_connection(self, address):
        # Split address into host and port
        try:
            host, port = address.split(':')
            port = int(port)
        except ValueError:
            print(f"Invalid address format: {address}. Expected format: host:port")
            return

        def tcp_handler():
            print(f"Starting TCP connection to {host}:{port}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                sock.connect((host, port))
                print(f"Connected to {host}:{port}")
                self.tcp_running = True
                
                while self.tcp_running:
                    try:
                        data = sock.recv(1024)
                        if not data:
                            print("Connection closed by server")
                            break
                        json_data = data.decode()
                        print(f"Received data: {json_data}")

                        # Parse JSON data
                        parsed_data = json.loads(json_data)
                        print(parsed_data)
                        self.update_config_file(parsed_data)

                    except socket.error as e:
                        print(f"Socket error: {e}")
                        break
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON: {e}")
                        
            except socket.error as e:
                print(f"Failed to connect: {e}")
            finally:
                sock.close()
                print("TCP connection closed")
                self.tcp_running = False

        # Stop existing connection if any
        self.stop_tcp_connection()
        
        # Start new connection thread
        self.tcp_thread = threading.Thread(target=tcp_handler)
        self.tcp_thread.daemon = True  # Thread will exit when main program exits
        self.tcp_thread.start()

    def stop_tcp_connection(self):
        if self.tcp_running:
            self.tcp_running = False
            if self.tcp_thread:
                self.tcp_thread.join(timeout=2.0)

    def update_config_file(self, new_data):
        config_file_path = './ringring.conf'
        config_data = {}

        # Check if the config file exists
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r') as f:
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError:
                    print("Failed to decode existing JSON config file. Starting fresh.")

        print(f"Config data: {config_data}")

        # Update the config data with new fields
        config_data.update(new_data)

        # Write the updated config data back to the file
        with open(config_file_path, 'w') as f:
            json.dump(config_data, f, indent=4)
            print(f"Updated configuration written to {config_file_path}")

    def check_and_write_config(self):
        # Get values from all characteristics
        wifiSSID = self.ssid_char.get_value_string()
        wifiPassword = self.password_char.get_value_string()
        appAddress = self.address_char.get_value_string()
        
        # Check if all values are set (not empty)
        if wifiSSID and wifiPassword and appAddress:
            print(f'Writing WiFi config - SSID: {wifiSSID}, Password: {wifiPassword}, App Address: {appAddress}')
            
            # Create a dictionary for the WiFi configuration
            wifi_config = {
                'wifiPassword': wifiPassword,
                'wifiSSID': wifiSSID
            }
            
            # Update the configuration file using the existing method
            self.update_config_file(wifi_config)

            # Start TCP connection after writing config
            self.start_tcp_connection(appAddress)

class SSIDCharacteristic(Characteristic):
    SSID_UUID = '00002222-e78c-7da4-b183-1b46ca5541a9'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.SSID_UUID,
            ['write'],
            service)
        self.value = bytes("", "utf-8")
    
    def get_value_string(self):
        return self.value.decode('utf-8')
    
    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        self.value = bytes(value)
        print(f'SSID set to: {self.get_value_string()}')
        self.service.check_and_write_config()

class PasswordCharacteristic(Characteristic):
    PASSWORD_UUID = '00003333-e78c-7da4-b183-1b46ca5541a9'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.PASSWORD_UUID,
            ['write'],
            service)
        self.value = bytes("", "utf-8")
    
    def get_value_string(self):
        return self.value.decode('utf-8')
    
    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        self.value = bytes(value)
        print(f'Password set {self.get_value_string()}')
        self.service.check_and_write_config()

class AddressCharacteristic(Characteristic):
    ADDRESS_UUID = '00004444-e78c-7da4-b183-1b46ca5541a9'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.ADDRESS_UUID,
            ['write'], 
            service)
        self.value = bytes("", "utf-8")
    
    def get_value_string(self):
        return self.value.decode('utf-8')
    
    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        self.value = bytes(value)
        print(f'Address set to: {self.get_value_string()}')
        self.service.check_and_write_config()

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
    wifi_service = WifiService(bus, 0)
    app.add_service(wifi_service)

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
    advertisement.add_service_uuid(WifiService.WIFI_UUID)
    advertisement.add_local_name("WiFiConfig")

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
        # Stop TCP connection
        wifi_service.stop_tcp_connection()
        
        # Unregister advertisement
        ad_manager.UnregisterAdvertisement(advertisement.get_path())
        print('Advertisement unregistered')
        dbus.service.Object.remove_from_connection(advertisement)
        
if __name__ == '__main__':
    main()