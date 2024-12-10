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
        self.listeners = []

    def set(self, key, value, suppress=None):
        """
        Set a key-value pair in the global state.

        :param key: Key to set.
        :param value: Value to set.
        :param suppress_listeners: A list of listeners to suppress notifications for (optional).
        """
        old_value = self.state.get(key)
        if old_value != value:
            self.state[key] = value
            for listener in self.listeners:
                if suppress and listener in suppress:
                    continue
                listener(key, old_value, value)

    def get(self, key):
        """Get the value associated with a key."""
        return self.state.get(key, None)

    def add_listener(self, callback):
        """Register a callback to be notified of state changes."""
        if callback not in self.listeners:
            self.listeners.append(callback)

    def remove_listener(self, callback):
        """Unregister a callback."""
        if callback in self.listeners:
            self.listeners.remove(callback)