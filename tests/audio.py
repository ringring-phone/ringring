import pjsua2 as pj
import ctypes

# Try to use specific device path
def test_specific_device():
    # Create endpoint configuration
    ep_cfg = pj.EpConfig()
    ep_cfg.medConfig.channelCount = 2
    ep_cfg.medConfig.clockRate = 16000
    ep_cfg.medConfig.audioFramePtime = 20
    ep_cfg.medConfig.maxMediaPorts = 254

    # Create and initialize PJSUA2
    print("\nCreating endpoint...")
    ep = pj.Endpoint()
    ep.libCreate()

    # Try to force ALSA initialization
        # try:
        #     # Try to explicitly set ALSA devices
        #     pj.pjmedia_aud_alsa_set_devices(ep, 1, ["plughw:3,0"])
        # except Exception as e:
        #     print(f"Error setting ALSA devices: {e}")

    print("\nInitializing endpoint...")
    ep.libInit(ep_cfg)

    print("\nStarting PJSUA...")
    ep.libStart()

    try:
        audio_mgr = ep.audDevManager()
        audio_mgr.refreshDevs()
        
        # Get device count
        num_devices = audio_mgr.getDevCount()
        print(f"\nFound {num_devices} devices:")
        
        for i in range(num_devices):
            try:
                dev_info = audio_mgr.getDevInfo(i)
                print(f"\nDevice {i}: {dev_info.name}")
                print(f"    Driver: {dev_info.driver}")
                print(f"    Input count: {dev_info.inputCount}")
                print(f"    Output count: {dev_info.outputCount}")
            except Exception as e:
                print(f"Error getting device {i} info: {e}")

    except Exception as e:
        print(f"Error in audio initialization: {e}")

    print("\nShutting down...")
    ep.libDestroy()

if __name__ == "__main__":
    test_specific_device()