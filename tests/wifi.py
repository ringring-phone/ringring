import pywifi
from pywifi import const
from time import sleep

def scan_wifi():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]  # Select the first wireless interface
    
    # Ensure the interface is activated
    iface.disconnect()
    sleep(1)  # Allow time for disconnection
    assert iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]
    
    iface.scan()  # Trigger a scan
    sleep(2)  # Wait for the scan to complete
    scan_results = iface.scan_results()
    
    networks = []
    for network in scan_results:
        networks.append(network.ssid)
    return networks

print("Scanning for Wi-Fi networks...")
wifi_networks = scan_wifi()
if wifi_networks:
    for idx, network in enumerate(wifi_networks, start=1):
        print(f"{idx}. {network}")
else:
    print("No networks found.")