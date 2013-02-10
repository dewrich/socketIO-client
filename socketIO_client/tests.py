from socketIO_client import SocketIO, BaseNamespace
from time import sleep
from unittest import TestCase


PAYLOAD = {'bbb': 'ccc'}
ON_RESPONSE_CALLED = False


class TestSocketIO(TestCase):

    def test_disconnect(self):
        socketIO = SocketIO('localhost', 8000)
        socketIO.disconnect()
        self.assertEqual(socketIO.connected, False)

    def test_emit(self):
        socketIO = SocketIO('localhost', 8000, Namespace)
        socketIO.emit('aaa')
        sleep(0.5)
        self.assertEqual(socketIO._namespace.payload, '')

    def test_emit_with_payload(self):
        socketIO = SocketIO('localhost', 8000, Namespace)
        socketIO.emit('aaa', PAYLOAD)
        sleep(0.5)
        self.assertEqual(socketIO._namespace.payload, PAYLOAD)

    def test_emit_with_callback(self):
        global ON_RESPONSE_CALLED
        ON_RESPONSE_CALLED = False
        socketIO = SocketIO('localhost', 8000)
        socketIO.emit('aaa', PAYLOAD, on_response)
        socketIO.wait(forCallbacks=True)
        self.assertEqual(ON_RESPONSE_CALLED, True)

    def test_events(self):
        global ON_RESPONSE_CALLED
        ON_RESPONSE_CALLED = False
        socketIO = SocketIO('localhost', 8000)
        socketIO.on('ddd', on_response)
        socketIO.emit('aaa', PAYLOAD)
        sleep(0.5)
        self.assertEqual(ON_RESPONSE_CALLED, True)

    def test_channels(self):
        mainSocket = SocketIO('localhost', 8000, Namespace)
        chatSocket = mainSocket.connect('/chat', Namespace)
        newsSocket = mainSocket.connect('/news', Namespace)
        newsSocket.emit('aaa', PAYLOAD)
        sleep(0.5)
        self.assertNotEqual(mainSocket._namespace.payload, PAYLOAD)
        self.assertNotEqual(chatSocket._namespace.payload, PAYLOAD)
        self.assertEqual(newsSocket._namespace.payload, PAYLOAD)

    def test_delete(self):
        socketIO = SocketIO('localhost', 8000)
        childThreads = [
            socketIO._heartbeatThread,
            socketIO._namespaceThread,
        ]
        del socketIO
        for childThread in childThreads:
            self.assertEqual(True, childThread.done.is_set())


class Namespace(BaseNamespace):

    payload = None

    def on_ddd(self, data=''):
        self.payload = data


def on_response(*args):
    global ON_RESPONSE_CALLED
    ON_RESPONSE_CALLED = True
