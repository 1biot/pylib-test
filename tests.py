import unittest
from unittest.mock import Mock
from mqtt_topic_callback import EventEmitter, Matcher, TopiCallbackHandler

TestClient = Mock()
TestClient.subscribe.return_value = True


class TestEventEmitter(unittest.TestCase):

    def test_add_event_callback_no_function(self):
        emitter = EventEmitter()
        self.assertIs(emitter.on(event_name='test_event', function=None), False)
        self.assertIs(emitter.on(event_name='test_event', function='None'), False)
        self.assertIs(emitter.on(event_name='test_event', function=6), False)
        self.assertIs(emitter.on(event_name='test_event', function={}), False)
        self.assertIs(emitter.on(event_name='test_event', function=[]), False)
        self.assertIs(emitter.on(event_name='test_event', function=()), False)
        self.assertEqual(len(emitter), 0)

    def test_add_event_callback(self):
        emitter = EventEmitter()
        self.assertIs(emitter.on(event_name='test_event', function=self.mock), True)
        self.assertEqual(len(emitter), 1)

    def test_remove_event_callback_no_function(self):
        emitter = EventEmitter()
        self.assertIs(emitter.off(event_name='test_event', function=None), False)
        self.assertIs(emitter.off(event_name='test_event', function='None'), False)
        self.assertIs(emitter.off(event_name='test_event', function=6), False)
        self.assertIs(emitter.off(event_name='test_event', function={}), False)
        self.assertIs(emitter.off(event_name='test_event', function=[]), False)
        self.assertIs(emitter.off(event_name='test_event', function=()), False)

    def test_remove_event_does_not_exists(self):
        emitter = EventEmitter()
        self.assertIs(emitter.off(event_name='test_event', function=lambda context: None), False)
        self.assertIs(emitter.off(event_name='test_event', function=self.mock), False)

    def test_remove_event(self):
        emitter = EventEmitter()
        emitter.on(event_name='test_event', function=self.mock)
        self.assertIs(emitter.off(event_name='test_event', function=self.mock), True)
        self.assertEqual(len(emitter), 0)

    def test_emmit(self):
        emitter = EventEmitter()
        emitter.on(event_name='test_event', function=self.mock)
        emitter.on(event_name='test_event_2', function=self.another_mock)
        emitter.emit(event_name='test_event')
        emitter.emit(event_name='test_event_2', context=('subscribed_topic', 'topic', 'payload'))

    def mock(self, context=1):
        self.assertEqual(context, 1)

    def another_mock(self, context):
        subscribed_topic, incoming_topic, payload = context
        self.assertIn(subscribed_topic, 'subscribed_topic')
        self.assertIn(incoming_topic, 'topic')
        self.assertIn(payload, 'payload')


class TesMqttMatcher(unittest.TestCase):

    def test_no_match(self):
        false_list = [
            Matcher("foo", "bar"),
            Matcher("foo", "FOO"),
            Matcher("foo/bar", "foo/bar/baz"),
            Matcher("foo/#", "fooo/abcd/bar/1234"),
            Matcher("+/+", "foo"),
            Matcher("+", "/foo"),
            Matcher('foo/+/#', 'foo'),
            Matcher('$share/group1/foo/bar', 'foo/bar/baz'),
            Matcher('$share/group1/+', 'foo'),
        ]

        for matcher in false_list:
            self.assertFalse(matcher.match())

    def test_match(self):
        true_list = [
            Matcher('foo', 'foo'),
            Matcher('foo/bar', 'foo/bar'),
            Matcher('foo/BAR', 'foo/BAR'),
            Matcher('foo/+', 'foo/bar'),
            Matcher('foo/+', 'foo/'),
            Matcher('foo/bar/+', 'foo/bar/baz'),
            Matcher('foo/+/bar/+', 'foo/abcd/bar/1234'),
            Matcher('foo/#', 'foo/abcd/bar/1234'),
            Matcher('foo/#', 'foo'),
            Matcher('foo/+/bar/#', 'foo/abcd/bar/1234/fooagain'),
            Matcher('+/+', 'foo/bar'),
            Matcher('+/#', 'foo/bar/baz'),
            Matcher('#', 'foo/bar/baz'),
            Matcher('/+', '/foo'),
            Matcher('+/+', '/foo'),
            Matcher('$share/group1/+', 'foo', True),
            Matcher('$share/group1/foo/bar', 'foo/bar', True),
            Matcher('$share/group1/+/+', '/foo', True),
        ]

        for matcher in true_list:
            self.assertTrue(matcher.match())


class TestMqttTopiCallbackHandler(unittest.TestCase):

    def test_add_topic_handler_without_callback(self):
        mqtch = TopiCallbackHandler()
        self.assertFalse(mqtch.add_topic_handler("topic", callback=None))

    def test_add_topic_handler_with_callback(self):
        mqtch = TopiCallbackHandler()
        self.assertTrue(mqtch.add_topic_handler("topic", callback=self.mock))

    def test_remove_handler_when_more_topic_handlers(self):
        test_lambda = lambda context: None
        mqtch = TopiCallbackHandler()
        self.assertTrue(mqtch.add_topic_handler("topic", callback=self.mock))
        self.assertEqual(len(mqtch), 1)
        self.assertTrue(mqtch.add_topic_handler("topic", callback=test_lambda))
        self.assertEqual(len(mqtch), 1)
        mqtch.remove_topic_handler("topic", callback=test_lambda)
        self.assertEqual(len(mqtch), 1)
        mqtch.remove_topic_handler("topic", callback=self.mock)
        self.assertEqual(len(mqtch), 0)

    def test_get_subscriptions(self):
        mqtch = TopiCallbackHandler()
        self.assertTrue(mqtch.add_topic_handler("topic", callback=self.mock))
        self.assertTrue(mqtch.add_topic_handler("topic2", callback=lambda context: None))
        self.assertEqual(len(mqtch.get_subscriptions()), 2)
        self.assertDictEqual(mqtch.get_subscriptions(), {"topic": 0, "topic2": 0})

    def test_remove_topic_handler(self):
        mqtch = TopiCallbackHandler()
        mqtch.add_topic_handler("topic", callback=self.mock)
        mqtch.remove_topic_handler("topic", callback=self.mock)
        self.assertEqual(len(mqtch), 0)

    def test_subscribe_no_client(self):
        mqtch = TopiCallbackHandler()
        with self.assertRaises(AttributeError):
            mqtch.subscribe(client=None)

    def test_subscribe(self):
        mqtch = TopiCallbackHandler()
        mqtch.add_topic_handler("topic", self.mock)
        self.assertEqual(mqtch.subscribe(client=TestClient()), True)

    def test_callbacks(self):
        mqtch = TopiCallbackHandler()
        mqtch.add_topic_handler("topic/#", self.mock)
        mqtch.process_incoming_topic("topic/from/broker", "payload-from-broker")

    def mock(self, context):
        self.assertTupleEqual(context, ("topic/#", "topic/from/broker", "payload-from-broker"))

