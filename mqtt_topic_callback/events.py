

class EventEmitter:

    def __init__(self):
        self._callbacks = {}

    def on(self, event_name, function):
        if not callable(function):
            return False

        self._callbacks[event_name] = self._callbacks.get(event_name, []) + [function]
        return True

    def emit(self, event_name, *args, **kwargs):
        return [function(*args, **kwargs) for function in self._callbacks.get(event_name, [])]

    def off(self, event_name, function):
        if not callable(function):
            return False

        if event_name not in self._callbacks.keys():
            return False

        event_callbacks = self._callbacks.get(event_name, [])
        for i in range(event_callbacks.count(function)):
            event_callbacks.remove(function)

        if not event_callbacks:
            del self._callbacks[event_name]
        else:
            self._callbacks[event_name] = event_callbacks

        return True

    def __len__(self):
        return len(self._callbacks)
