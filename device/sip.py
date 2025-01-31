import time
import json
import logging
import threading
import pjsua2 as pj
from global_state import GlobalState, State

CONFIG_PATH = "../config.json"
PHONE_NUMBER = "phoneNumber"
PASSWORD = "password"
SIP_IP = "sipIP"
AUDIO_DEVICE = 6

calls = []

class MyCall(pj.Call):
    def __init__(self, acc, call_id, endpoint):
        pj.Call.__init__(self, acc, call_id)
        self.endpoint = endpoint

    def onCallState(self, prm):
        call_info = self.getInfo()
        if call_info.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            logging.debug("Call disconnected")
            self.terminate()
            GlobalState().set(State.IN_CALL, False)
            GlobalState().set(State.RINGING, False)

    def onCallMediaState(self, prm):
        call_info = self.getInfo()
        for mi in call_info.media:
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                logging.debug("Call connected")
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

    def terminate(self):
        call_prm = pj.CallOpParam()
        call_prm.statusCode = 200
        self.hangup(call_prm)

class MyAccount(pj.Account):
    def __init__(self, endpoint):
        pj.Account.__init__(self)
        self.endpoint = endpoint

    def onIncomingCall(self, prm):
        logging.debug(f"Incoming call {prm.callId}")
        globals = GlobalState()

        call = MyCall(self, prm.callId, self.endpoint)
        call_prm = pj.CallOpParam()
        call_prm.statusCode = 180
        call.answer(call_prm)
        calls.append(call)

        globals.set(State.RINGING, True)

        def ringing():
            while globals.get(State.ON_THE_HOOK):
                time.sleep(0.01)

            globals.set(State.RINGING, False)
            globals.set(State.IN_CALL, True)

            call_prm.statusCode = 200
            call.answer(call_prm)
        
        thread = threading.Thread(target=ringing)
        thread.start()

    def makeCall(self, dest_uri):
        logging.debug(f"makeCall: {dest_uri}")
        try:
            call_prm = pj.CallOpParam()
            call = MyCall(self, pj.PJSUA_INVALID_ID, self.endpoint)
            call.makeCall(dest_uri, call_prm)
            print(f"Call initiated to {dest_uri}")

            calls.append(call)
        except Exception as e:
            print(f"Error making call: {e}")

def sip():
    config = {
        PHONE_NUMBER: "",
        PASSWORD: "",
        SIP_IP: ""
    }

    while True:
        try:
            with open(CONFIG_PATH, "r") as file:
                data = json.load(file)
            print("Config file loaded successfully!")
            config[PHONE_NUMBER] = data[PHONE_NUMBER]
            config[PASSWORD] = data[PASSWORD]
            config[SIP_IP] = data[SIP_IP]
            break
        except FileNotFoundError:
            print(f"File {CONFIG_PATH} not found. Retrying in 5 seconds...")
        except json.JSONDecodeError:
            print(f"File {CONFIG_PATH} is not a valid JSON file. Retrying in 5 seconds...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Retrying in 5 seconds...")

        time.sleep(5)

    # Initialize the library
    ep = pj.Endpoint()
    ep.libCreate()

    # Configure and initialize the endpoint
    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig.level = 1

    media_cfg = pj.MediaConfig()
    media_cfg.clockRate = 44100  # Match sound card sample rate
    media_cfg.channelCount = 1   # Mono
    media_cfg.audioFramePtime = 20  # 20 ms frame time (common for VoIP)
    media_cfg.sndClockRate = 44100  # Align sound device clock rate
    ep.mediaConfig = media_cfg

    ep.libInit(ep_cfg)

    # Set USB sound card as default (replace dev_id with your USB sound card ID)
    ep.audDevManager().setCaptureDev(AUDIO_DEVICE)
    ep.audDevManager().setPlaybackDev(AUDIO_DEVICE)

    sip_transport_cfg = pj.TransportConfig()
    sip_transport_cfg.port = 5060
    tcp_transport_id = ep.transportCreate(pj.PJSIP_TRANSPORT_TCP, sip_transport_cfg)

    # Start SIP endpoint
    ep.libStart()

    # Configure account
    acc_cfg = pj.AccountConfig()
    acc_cfg.idUri = f"sip:{config[PHONE_NUMBER]}@{config[SIP_IP]}:5060;transport=tcp"
    acc_cfg.regConfig.registrarUri = f"sip:{config[SIP_IP]}"
    acc_cfg.sipConfig.authCreds.append(pj.AuthCredInfo("digest", "*", config[PHONE_NUMBER], 0, config[PASSWORD]))
    acc_cfg.sipConfig.transportId = tcp_transport_id

    # Create account
    account = MyAccount(ep)
    account.create(acc_cfg)
    
    globals = GlobalState()
    while True:
        command = globals.getCommand()
        if command != None:
            if not globals.get(State.ON_THE_HOOK) and len(command) == 4:
                account.makeCall(f"sip:{command}@{config[SIP_IP]}:5060;transport=tcp")

        if globals.get(State.ON_THE_HOOK) and globals.get(State.IN_CALL):
            calls[0].terminate()
            calls.pop()

        time.sleep(0.01)

if __name__ == "__main__":
    try:
        sip()
    except KeyboardInterrupt:
        logging.warning("Exiting program via keyboard interrupt.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")