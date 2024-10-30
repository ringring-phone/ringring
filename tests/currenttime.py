import pjsua2 as pj
import pyttsx3
import time
import tempfile
import os
from datetime import datetime
from pydub import AudioSegment

calls = []

class MyCall(pj.Call):
    def __init__(self, account, call_id=pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, account, call_id)
        print("===========================================================")
        print(f"**** MyCall constructor {call_id} {self.getInfo().state}")

    def onCallState(self, prm):
        call_info = self.getInfo()
        print("===========================================================")
        print(f"**** Call state is {call_info.stateText}, last code = {call_info.lastStatusCode} ({call_info.lastReason})")
        if call_info.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            print("===========================================================")
            print("**** Call disconnected")
        elif call_info.state == pj.PJSIP_INV_STATE_CONFIRMED:
            print("===========================================================")
            print("**** Call is active and confirmed")
            self.send_time_message()

    def onCallMediaState(self, prm):
        call_info = self.getInfo()
        print("===========================================================")
        print("**** onCallMediaState triggered")
        for media in call_info.media:
            if media.type == pj.PJMEDIA_TYPE_AUDIO and self.hasMedia():
                print("===========================================================")
                print("**** Audio media is active")
                aud_med = self.getAudioMedia(0)
                # Get and print audio media port information
                port_info = aud_med.getPortInfo()
                print("===========================================================")
                print(f"**** RTP audio at port: {port_info.portId}, name: {port_info.name}")

    def send_time_message(self):
        # Generate the current time message using pyttsx3
        engine = pyttsx3.init(driverName='espeak')
        engine.setProperty('rate', 100)
        current_time = datetime.now().strftime("%H:%M")
        message = f"The current time is {current_time}"

        # Create a temporary file for the WAV output
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
            temp_file_path = temp_wav_file.name

        try:
            # Save the voice message to the temp file
            engine.save_to_file(message, temp_file_path)

            # Ensure the file is completely written
            engine.runAndWait()

            # Wait until the file has a non-zero size
            timeout = 5  # 5 seconds timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                if os.path.getsize(temp_file_path) > 0:
                    break
                time.sleep(0.1)  # Check every 100 ms
            
            # Check if the file has non-zero size before attempting playback
            if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
                print(f"Original WAV file created: {temp_file_path}")

                # Load and resample the audio to 16 kHz
                audio = AudioSegment.from_wav(temp_file_path)
                audio = audio.set_frame_rate(16000)

                # Save the resampled file
                resampled_wav_path = temp_file_path.replace(".wav", "_16kHz.wav")
                audio.export(resampled_wav_path, format="wav")
                print(f"Resampled WAV file: {resampled_wav_path}")

                # Play the resampled WAV file
                media = pj.AudioMediaPlayer()
                media.createPlayer(resampled_wav_path, pj.PJMEDIA_FILE_NO_LOOP)

                # Transmit the audio to the call's media
                call_media = self.getAudioMedia(0)  # Use the first media stream (index 0)
                media.startTransmit(call_media)

                # Calculate the duration of the audio in milliseconds
                duration_ms = len(audio)
                print(f"Audio duration: {duration_ms} ms")

                # Wait for the duration of the audio to complete playback
                duration = duration_ms / 1000
                print("===========================================================")
                print(f"sleep for {duration}")
                time.sleep(duration)
            else:
                print("Error: Temporary WAV file is empty or not found.")
        except Exception as e:
            print(f"Error playing message: {e}")
        finally:
            # Clean up the temporary file
            # if os.path.exists(temp_file_path):
            #     os.remove(temp_file_path)
            
            print("===========================================================")
            # Ensure call state is CONFIRMED before hanging up
            call_info = self.getInfo()
            if call_info.state == pj.PJSIP_INV_STATE_CONFIRMED:
                print("===========================================================")
                print("Hanging up the call")
                call_op_param = pj.CallOpParam()
                call_op_param.statusCode = pj.PJSIP_SC_OK
                self.hangup(call_op_param)
            else:
                print("Cannot hang up, call is not in CONFIRMED state.")

class Account(pj.Account):
    def __init__(self):
        pj.Account.__init__(self)

    def onRegState(self, prm):
        acc_info = self.getInfo()
        print("===========================================================")
        print("**** Account registration state is", acc_info.regIsActive)

    def onIncomingCall(self, prm):
        call = MyCall(self, call_id=prm.callId)

        # Send 180 Ringing
        call_op_param = pj.CallOpParam()
        call_op_param.statusCode = pj.PJSIP_SC_RINGING
        call.answer(call_op_param)
        print("===========================================================")
        print(f"**** Incoming call from {call.getInfo().remoteUri}")

        # # Wait for 2 seconds before sending 200 OK
        time.sleep(2)

        # Send 200 OK
        call_op_param.statusCode = pj.PJSIP_SC_OK
        try:
            call.answer(call_op_param)
            print("===========================================================")
            print("**** Call answered with 200 OK")
        except Exception as e:
            print(f"Failed to answer call: {e}")

        calls.append(call)

# Main program
try:
    ep = pj.Endpoint()
    ep.libCreate()

    # Set up log configuration
    log_cfg = pj.LogConfig()
    log_cfg.level = 5
    log_cfg.consoleLevel = 5

    ep_cfg = pj.EpConfig()
    ep_cfg.logConfig = log_cfg

    # Set STUN and ICE configuration
    stun_servers = pj.StringVector()
    stun_servers.append("stun.zoiper.com:3478")
    # stun_servers.append("stun.l.google.com:19302")
    # ep_cfg.uaConfig.stunServer = stun_servers
    # ep_cfg.medConfig.enableIce = True


    ep.libInit(ep_cfg)

    # Transport setup
    sip_transport_cfg = pj.TransportConfig()
    sip_transport_cfg.port = 5060
    tcp_transport_id = ep.transportCreate(pj.PJSIP_TRANSPORT_TCP, sip_transport_cfg)

    ep.libStart()

    # Set Null Audio Device for headless operation
    ep.audDevManager().setNullDev()
    # Set G722 codec to highest priority
    # codecs = ep.codecEnum2()
    # for codec in codecs:
    #     print("===========================================================")
    #     print(f"{codec.codecId}")
    #     if codec.codecId == "G722/16000/1":
    #         print("===========================================================")
    #         print(f"Setting priority for {codec.codecId}")
    #         ep.codecSetPriority(codec.codecId, 255)
    #     else:
    #         ep.codecSetPriority(codec.codecId, 128)

    print("===========================================================")
    print("**** SIP stack started")

    # Register account
    acc_cfg = pj.AccountConfig()
    acc_cfg.idUri = "sip:9000@10.11.21.228:5060;transport=tcp"
    acc_cfg.regConfig.registrarUri = "sip:10.11.21.228"
    acc_cfg.sipConfig.authCreds.append(pj.AuthCredInfo("digest", "*", "9000", 0, "9000"))
    acc_cfg.sipConfig.transportId = tcp_transport_id  # Use the created TCP transport ID
    # acc_cfg.sipConfig.proxies.append("sip:sip10.ringcentral.com:5090;transport=tcp")
    # acc_cfg.idUri = "sip:16505073501@sip.ringcentral.com:5060;transport=tcp"
    # acc_cfg.regConfig.registrarUri = "sip:sip.ringcentral.com"
    # acc_cfg.sipConfig.authCreds.append(pj.AuthCredInfo("digest", "*", "803528303016", 0, "VSsvx"))
    # acc_cfg.sipConfig.proxies.append("sip:sip10.ringcentral.com:5090;transport=tcp")

    acc_cfg.mediaConfig.enableIce = True
    acc_cfg.mediaConfig.srtpUse = 0
    acc_cfg.mediaConfig.noMedia = False

    account = Account()
    account.create(acc_cfg)

    while True:
        time.sleep(10)
        print("===========================================================")
        print("loop")

# Run the program until user input
#input("Press Enter to quit...\n")

finally:
    # Clean up
    print("===========================================================")
    print("Cleaning up")
    ep.libDestroy()

# Manual Provisioning
# To connect your device with RingCentral services, setup your device following the steps below. Configuration for each device may vary, please check with your device’s manufacturer for specific instructions.

# Step 1: Secure voice transport: No
# Step 2: Configure SIP information

# SIP Domain              sip.ringcentral.com:5060
# Remote SIP port         5060
# Local SIP port          5060
# Outbound Proxy          SIP10.ringcentral.com:5090
# Outbound Proxy Port     5090
# User Name               16505073501
# Password                VSsvx
# Authorization ID        803528303016
