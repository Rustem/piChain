from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.task import deferLater

import time


TXN_MAX_COUNT = 500
txn_count = 0
started = False
start_time = None
end_time = None


class Connection(LineReceiver):

    def lineReceived(self, line):
        global start_time
        global end_time
        global txn_count

        print(line.decode())
        if not started:
            start_time = time.time()

        txn_count += 1
        if txn_count == TXN_MAX_COUNT:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print('elapsed time = %s' % str(elapsed_time))

    def rawDataReceived(self, data):
        pass

    def connectionMade(self):

        for i in range(0, TXN_MAX_COUNT):
            msg = 'put k%s v' % str(i)
            deferLater(reactor, i/100, self.sendLine, msg.encode())


class ClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        print('Resetting reconnection delay')
        self.resetDelay()
        return Connection()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


reactor.connectTCP('localhost', 8000, ClientFactory())
reactor.run()
