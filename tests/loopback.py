import pjsua2 as pj

# Main program
try:
    # Initialize the library
    ep = pj.Endpoint()
    ep.libCreate()

    # Configure and initialize the endpoint
    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig.consoleLevel = 4

    ep.libInit(ep_cfg)

    # Refresh and list audio devices
    ep.audDevManager().refreshDevs()
    dev_count = ep.audDevManager().getDevCount()
    print("Available Audio Devices:")
    for idx in range(dev_count):
        dev_info = ep.audDevManager().getDevInfo(idx)
        print(f"[{idx}] {dev_info.name} (ID: {idx})")

    # Set USB sound card for capture and playback
    ep.audDevManager().setCaptureDev(6)
    ep.audDevManager().setPlaybackDev(6)

    # Start the PJSUA2 library
    ep.libStart()
    print("PJSUA2 endpoint started")

    # Perform loopback: connect capture (microphone) to playback (speaker)
    audio_capture = ep.audDevManager().getCaptureDevMedia()
    audio_playback = ep.audDevManager().getPlaybackDevMedia()
    audio_playback.adjustRxLevel(1.5) 

    print("Starting loopback test: microphone to speaker...")
    audio_capture.startTransmit(audio_playback)

    # Keep the program running for the test
    input("Press Enter to stop the loopback test...\n")

    # Stop the loopback
    audio_capture.stopTransmit(audio_playback)
    print("Loopback test stopped")

    # Clean up
    ep.libDestroy()
    print("PJSUA2 endpoint destroyed")

except Exception as e:
    print(f"Exception: {e}")