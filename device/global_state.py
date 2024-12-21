import queue

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Create a new instance if one does not already exist
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class GlobalState(metaclass=SingletonMeta):
    def __init__(self):
        self.state = {}
        self.queue = queue.Queue()

    def set(self, key, value):
        old_value = self.state.get(key)
        if old_value != value:
            self.state[key] = value

    def get(self, key):
        return self.state.get(key, None)
    
    def addCommand(self, command):
        print(f"GlobalState.addCommand {command}")
        self.queue.put(command)

    def getCommand(self):
        try:
            return self.queue.get(block=False)
        except queue.Empty:
            return None

class State:
    REGISTERED_WITH_SIP = "registered_with_sip"
    CALL_ACTIVE = "call_active"
    RINGING = "ringing"