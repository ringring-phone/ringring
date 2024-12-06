import pjsua2 as pj

calls = []

class MyCall(pj.Call):
    def __init__(self, acc, call_id, endpoint):
        pj.Call.__init__(self, acc, call_id)
        self.endpoint = endpoint

    def onCallState(self, prm):
        call_info = self.getInfo()
        print(f"Call State: {call_info.stateText}")
        if call_info.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            print("Call disconnected")
            self.hangup()

    def onCallMediaState(self, prm):
        call_info = self.getInfo()
        for mi in call_info.media:
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                m = self.getMedia(mi.index)
                am = pj.AudioMedia.typecastFromMedia(m)
                # Connect the call audio to the sound card
                print("Connecting call audio to USB sound card...")
                try:
                    self.endpoint.audDevManager().getCaptureDevMedia().startTransmit(am)
                    audio_playback = self.endpoint.audDevManager().getPlaybackDevMedia()
                    audio_playback.adjustRxLevel(1.5) 
                    am.startTransmit(audio_playback)
                except Exception as e:
                    print(f"Error connecting to USB sound card: {e}")

class MyAccount(pj.Account):
    def __init__(self, endpoint):
        pj.Account.__init__(self)
        self.endpoint = endpoint

    def onIncomingCall(self, prm):
        print("Incoming call received!")
        call = MyCall(self, prm.callId, self.endpoint)
        
        # Prepare the call answer parameters
        call_prm = pj.CallOpParam()
        call_prm.statusCode = 200  # Accept the call
        
        try:
            call.answer(call_prm)  # Accept the call with the parameters
            print("Call answered")

            calls.append(call)
        except Exception as e:
            print(f"Failed to answer call: {e}")

# Main program
try:
    # Initialize the library
    ep = pj.Endpoint()
    ep.libCreate()

    # Configure and initialize the endpoint
    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig.level = 4

    media_cfg = pj.MediaConfig()
    media_cfg.clockRate = 44100  # Match sound card sample rate
    media_cfg.channelCount = 1   # Mono
    media_cfg.audioFramePtime = 20  # 20 ms frame time (common for VoIP)
    media_cfg.sndClockRate = 44100  # Align sound device clock rate
    ep.mediaConfig = media_cfg

    ep.libInit(ep_cfg)

    # Configure and set audio devices
    ep.audDevManager().refreshDevs()
    dev_count = ep.audDevManager().getDevCount()
    print("Available Audio Devices:")
    for idx in range(dev_count):
        dev_info = ep.audDevManager().getDevInfo(idx)
        print(f"[{idx}] {dev_info.name} (ID: {idx})")


    # Set USB sound card as default (replace dev_id with your USB sound card ID)
    ep.audDevManager().setCaptureDev(6)
    ep.audDevManager().setPlaybackDev(6)

    sip_transport_cfg = pj.TransportConfig()
    sip_transport_cfg.port = 5060
    tcp_transport_id = ep.transportCreate(pj.PJSIP_TRANSPORT_TCP, sip_transport_cfg)

    # Start SIP endpoint
    ep.libStart()
    print("PJSUA2 endpoint started")

    # Configure account
    acc_cfg = pj.AccountConfig()
    acc_cfg.idUri = "sip:9000@10.11.21.228:5060;transport=tcp"
    acc_cfg.regConfig.registrarUri = "sip:10.11.21.228"
    acc_cfg.sipConfig.authCreds.append(pj.AuthCredInfo("digest", "*", "9000", 0, "9000"))
    acc_cfg.sipConfig.transportId = tcp_transport_id

    # Create account
    account = MyAccount(ep)
    account.create(acc_cfg)

    print("SIP account registered")
    print("Waiting for incoming calls...")

    # Keep the program running
    input("Press Enter to quit...\n")

    # Clean up
    ep.libDestroy()

except Exception as e:
    print(f"Exception: {e}")