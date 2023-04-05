from . import events


class Matcher:
    handle_share_subscription = False

    def __init__(self, tp, t, hss=False):
        self.topic_pattern = tp
        self.topic = t
        self.handle_share_subscription = hss

    def match(self):
        topic_pattern_list = self.topic_pattern.split('/')
        hss = self.handle_share_subscription
        ltpl = len(topic_pattern_list) > 2 and self.topic_pattern.startswith('$share/')
        if hss and ltpl:
            topic_pattern_list = topic_pattern_list[2::1]

        topic_array_list = self.topic.split('/')
        size_of_topic_pattern_list = len(topic_pattern_list)
        for i in range(size_of_topic_pattern_list):
            left = topic_pattern_list[i]
            try:
                right = topic_array_list[i]
            except IndexError:
                right = None

            if left == '#':
                return len(topic_array_list) >= size_of_topic_pattern_list - 1
            if left not in ('+', right):
                return False

        return size_of_topic_pattern_list == len(topic_array_list)


class TopiCallbackHandler(events.EventEmitter):

    def __init__(self):
        super().__init__()
        self.__subscriptions = {}

    def add_topic_handler(self, topic, callback, qos=0):
        if not callable(callback):
            return False

        self.on(topic, callback)
        self.__subscriptions[topic] = qos
        return True

    def remove_topic_handler(self, topic, callback=None):
        if callable(callback):
            self.off(event_name=topic, function=callback)

        if not super().__len__():
            if topic in self.__subscriptions.keys():
                del self.__subscriptions[topic]

    def get_subscriptions(self):
        return self.__subscriptions

    def subscribe(self, client):
        if not hasattr(client, 'subscribe') or not callable(client.subscribe):
            raise AttributeError("Client has no subscribe method")

        for subscribed_topic in self.__subscriptions:
            qos = self._get_qos(subscribed_topic)
            client.subscribe(subscribed_topic, qos)
        return True

    def process_incoming_topic(self, topic, payload):
        for subscribed_topic in self._callbacks:
            topic_matcher = Matcher(subscribed_topic, topic)
            if topic_matcher.match():
                self.emit(subscribed_topic, (subscribed_topic, topic, payload))

    def _get_qos(self, topic):
        return self.__subscriptions[topic] if self.__subscriptions[topic] else 0

    def __len__(self):
        return len(self.__subscriptions)
