"""This module contains test scenarios that are used as integration "tests" of PaxosLogic and PaxosNetwork.
All scenarios are based on three running nodes with node id 0,1 and 2.

basic behavior:
- Scenarios 1-6 test the healthy state.
- Scenarios 7-12 test each possible unhealthy state the system can be in.

crash behavior:
- Scenarios 20-21 test node crashes.

partition bahavior:
- Scenarios 30-

note: Can for example use Multirun plugin of pyCharm or write a script to start all nodes at exactly the same time,
this avoids the problem of initializing the state of the nodes at different times.

note: currently the tests only work locally
"""

import logging

from twisted.internet import reactor
from twisted.internet.task import deferLater

from piChain.messages import Transaction
from piChain.config import peers


class IntegrationScenarios:

    """ basic behavior:
    """

    @staticmethod
    def scenario1(node):
        """Start the paxos algorithm by bringing a Transaction in circulation. A node sends it directly to the single
        quick node.

        This scenario assumes a healthy state i.e one quick node and the others are slow.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 1')
        if node.id == 2:
            # create a Transaction and send it to node with id == 0 (the quick node)
            txn = Transaction(2, 'command1', 1)
            connection = node.peers.get(peers.get('0').get('uuid'))
            if connection is not None:
                logging.debug('txn send to node 0')
                connection.sendLine(txn.serialize())

    @staticmethod
    def scenario2(node):
        """Start the paxos algorithm by bringing a Transaction in circulation. A node broadcasts the transaction.

        This scenario assumes a healthy state i.e one quick node and the others are slow.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 2')

        if node.id == 2:
            # create a Transaction and broadcast it
            txn = Transaction(2, 'command1', 1)
            node.broadcast(txn, 'TXN')

    @staticmethod
    def scenario3(node):
        """A node brodcasts multiple transactions simultaneously.

        This scenario assumes a healthy state i.e one quick node and the others are slow.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 3')
        if node.id == 2:
            # create Transactions and broadcast them
            txn = Transaction(2, 'command1', 1)
            txn2 = Transaction(2, 'command2', 3)
            node.broadcast(txn, 'TXN')
            node.broadcast(txn2, 'TXN')

    @staticmethod
    def scenario4(node):
        """A node brodcasts multiple transactions with a short delay between them.

        This scenario assumes a healthy state i.e one quick node and the others are slow.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 4')
        if node.id == 2:
            # create Transactions and broadcast them
            txn = Transaction(2, 'command1', 1)
            txn2 = Transaction(2, 'command2', 2)
            node.broadcast(txn, 'TXN')

            deferLater(reactor, 1, node.broadcast, txn2, 'TXN')

    @staticmethod
    def scenario5(node):
        """Multiple nodes broadcast a transaction.

        This scenario assumes a healthy state i.e one quick node and the others are slow.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 5')
        if node.id == 2:
            # create a Transaction and broadcast it
            txn = Transaction(2, 'command1', 1)
            node.broadcast(txn, 'TXN')

        elif node.id == 1:
            # create a Transaction and broadcast it
            txn = Transaction(1, 'command2', 2)
            node.broadcast(txn, 'TXN')

            # create another Transaction and broadcast it
            txn3 = Transaction(1, 'command3', 3)
            node.broadcast(txn, 'TXN')
            deferLater(reactor, 1, node.broadcast, txn3, 'TXN')

    @staticmethod
    def scenario6(node):
        """Quick node broadcasts a transaction.

        This scenario assumes a healthy state i.e one quick node and the others are slow.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 6')
        if node.id == 0:
            # create a Transaction and broadcast it
            txn = Transaction(0, 'command1', 1)
            node.broadcast(txn, 'TXN')

    @staticmethod
    def scenario7(node):
        """Unhealthy state: q = 0 and m = 1. Medium node will create a block and promote itself. Thus we are in a
         healthy state again. Because the node is quick it will directly start a paxos instance.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 7')
        if node.id == 0:
            # medium node
            node.state = 1

        elif node.id == 1:
            # slow node
            node.state = 2

        elif node.id == 2:
            # slow node
            node.state = 2

            # create a Transaction and broadcast it
            txn = Transaction(2, 'command1', 1)
            deferLater(reactor, 0.1, node.broadcast, txn, 'TXN')

    @staticmethod
    def scenario8(node):
        """Unhealthy state: q = 1 and m > 1. Quick node will create a block which demotes other medium nodes. Thus
        we are back in a healthy state again.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 8')
        if node.id == 0:
            # quick node
            node.state = 0

        elif node.id == 1:
            # medium node
            node.state = 1

        elif node.id == 2:
            # medium node
            node.state = 1

            # create a Transaction and broadcast it
            txn = Transaction(2, 'command1', 1)
            deferLater(reactor, 0.1, node.broadcast, txn, 'TXN')

    @staticmethod
    def scenario9(node):
        """Unhealthy state: q = 0 and m = 0. At least one slow node will create a block. They will all promote to
        medium. If there are more than one they will see each others blocks and since only one is the deepest, all but
        one will demote to slow. The single medium node promotes to quick once it created another block.
        Thus we are eventually back in a healthy state.

        note: to test case where more than one slow nodes creates a block (simultaneously) remove random perturbation
        of patience of slow nodes.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 9')
        if node.id == 0:
            # slow node
            node.state = 2

        elif node.id == 1:
            # slow node
            node.state = 2

        elif node.id == 2:
            # slow node
            node.state = 2

            # create a Transaction and broadcast it
            txn = Transaction(2, 'command1', 1)
            deferLater(reactor, 0.1, node.broadcast, txn, 'TXN')

            # create another Transaction a little bit later and broadcast it
            txn2 = Transaction(2, 'command2', 2)
            deferLater(reactor, 1, node.broadcast, txn2, 'TXN')

    @staticmethod
    def scenario10(node):
        """Unhealthy state: q > 1. This scenario can happen because of a partition. The quick nodes will all
        create blocks immediately and start a paxos instance (here is where the consistency guarantee of paxos is
        needed because we have multiple paxos clients competing for their block to be committed).
        Since a receipt of a block created by a quick node results in demoting to slow, all nodes will demote to slow
        and we are in the scenario q = 0 / m = 0 described above. Thus we are eventually back in a healthy state.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 10')
        if node.id == 0:
            # quick node
            node.state = 0

        elif node.id == 1:
            # quick node
            node.state = 0

        elif node.id == 2:
            # quick node
            node.state = 0

            # create a Transaction and broadcast it
            txn = Transaction(2, 'command1', 1)
            deferLater(reactor, 0.1, node.broadcast, txn, 'TXN')

    @staticmethod
    def scenario11(node):
        """Unhealthy state: q > 1. This scenario can happen because of a partition. The quick nodes will all
        create blocks immediately and start a paxos instance (here is where the consistency guarantee of paxos is
        needed because we have multiple paxos clients competing for their block to be committed).
        Since a receipt of a block created by a quick node results in demoting to slow, all nodes will demote to slow
        and we are in the scenario q = 0 / m = 0 described above. Thus we are eventually back in a healthy state.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 11')
        if node.id == 0:
            # quick node
            node.state = 0

        elif node.id == 1:
            # quick node
            node.state = 0

        elif node.id == 2:
            # quick node
            node.state = 0

            # create a Transaction and broadcast it
            txn = Transaction(2, 'command1', 1)
            deferLater(reactor, 0.1, node.broadcast, txn, 'TXN')

            # create another Transaction a little bit later and broadcast it
            txn2 = Transaction(2, 'command2', 2)
            deferLater(reactor, 2, node.broadcast, txn2, 'TXN')

            # create another Transaction a little bit later and broadcast it
            txn3 = Transaction(2, 'command3', 3)
            deferLater(reactor, 4, node.broadcast, txn3, 'TXN')

    @staticmethod
    def scenario12(node):
        """Unhealthy state: q = 0 and m > 1. All the medium nodes will create a block and promote to quick. Since a
        receipt of a block where the creator state was quick demotes a node to slow, all nodes demote to slow and we
        are in scenario q = 0/m = 0 described above.  Thus we are eventually back in a healthy state.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 12')
        if node.id == 0:
            # medium node
            node.state = 1

        elif node.id == 1:
            # medium node
            node.state = 1

        elif node.id == 2:
            # medium node
            node.state = 1

            # create a Transaction and broadcast it
            txn = Transaction(2, 'command1', 1)
            node.broadcast(txn, 'TXN')
            deferLater(reactor, 0.1, node.broadcast, txn, 'TXN')

            # create another Transaction a little bit later and broadcast it
            txn2 = Transaction(2, 'command2', 2)
            deferLater(reactor, 2, node.broadcast, txn2, 'TXN')

            # create another Transaction a little bit later and broadcast it
            txn3 = Transaction(2, 'command3', 3)
            deferLater(reactor, 4, node.broadcast, txn3, 'TXN')

    """ crash behavior: 
    """

    @staticmethod
    def scenario20(node):
        """TestNode crashes. Crash a slow node after a commit.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 13')
        if node.id == 0:

            # create a Transaction and broadcast it
            txn = Transaction(0, 'command1', 1)
            node.broadcast(txn, 'TXN')
            deferLater(reactor, 0.1, node.broadcast, txn, 'TXN')

            # create another Transaction after crashed node recovered
            txn2 = Transaction(0, 'command2', 2)
            deferLater(reactor, 6, node.broadcast, txn2, 'TXN')

    @staticmethod
    def scenario21(node):
        """TestNode crashes. Crash the quick node after a commit.

        Args:
            node (Node): Node calling this method

        """
        logging.debug('start test scenario 14')
        if node.id == 1:

            # create a Transaction and broadcast it
            txn = Transaction(1, 'command1', 1)
            node.broadcast(txn, 'TXN')
            deferLater(reactor, 0.1, node.broadcast, txn, 'TXN')

            # create another Transaction after crashed node recovered
            txn2 = Transaction(1, 'command2', 2)
            deferLater(reactor, 6, node.broadcast, txn2, 'TXN')

    """ partition behavior: 
    """