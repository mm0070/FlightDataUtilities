import errno
import socket
import time


class MutexException(Exception):
    pass


class Mutex:
    """
    Provides an implementation of an application mutex using abstract sockets.

    Note: Abstract UNIX sockets are specific to Linux.

    Example code for using this mutex class::

        import sys

        from utilities.mutex import Mutex, MutexException

        def main():

            # Check whether we want to exit the running application:
            if '--exit' in sys.argv[1:]:
                Mutex.notify('APPLICATION', 'terminate')
                Mutex.wait('APPLICATION')  # block until it terminates.
                return 0

            # Attempt to acquire the mutex; handle any exceptions:
            try:
                mutex = Mutex('APPLICATION')
            except MutexException as error:
                print('[!] %s' % str(error), file=sys.stderr)
                return 1

            # Run the application loop checking for expected messages:
            try:
                while not mutex.receive('terminate'):
                    # ... execute application loop here.
                return 0

            # Always clean up the mutex when the application exits:
            finally:
                mutex.destroy()

            return 1

        if __name__ == '__main__':

            sys.exit(main())
    """

    def __init__(self, name):
        """
        Initialise a mutex utilising abstract UNIX sockets.

        The socket is set up to listen for connections over which messages can
        be sent, and the socket is made non-blocking.  This provides the
        ability for notifying the running instance of a request to shutdown or
        to focus its window if it is a GUI application, for example.

        Note: Abstract UNIX sockets are specific to Linux.

        :param name: The unique name for the socket.
        :type name: string
        :raises: MutexException -- when an instance already exists.
        :raises: OSError -- when a problem occurs with the mutex socket.
        """
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.socket.bind('\0%s' % name)
            self.socket.listen(1)
            self.socket.setblocking(0)
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                raise MutexException('An instance already exists.')
            raise

    def destroy(self):
        """Destroy the mutex by shutting down the abstract socket."""
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def receive(self, message, size=32):
        """
        Receives messages over the mutex abstract socket.

        Ignores OSError errors as a result of not receiving a connection on the
        non-blocking socket.

        :param message: A message to check for on the socket.
        :type messages: string
        :param size: The size of the buffer to use for receiving a message.
        :type size: integer
        :returns: Whether the message was received on the socket.
        :rtype: boolean
        :raises: OSError -- when a problem occurs while receiving.
        """
        try:
            connection = self.socket.accept()[0]
            # Check whether we have received the expected message:
            if connection.recv(size) == message:
                return True
        except BlockingIOError:
            # Ignore errors as a result of their being no connection:
            pass
        return False

    @staticmethod
    def notify(name, message):
        """
        Notifies an existing application instance via its mutex socket.

        :param name: The name of the mutex to notify.
        :type name: string
        :param message: The message to send to the application instance.
        :type message: string
        :returns: Whether the message was successfully sent.
        :rtype: boolean
        :raises: OSError -- when a problem occurs while sending.
        """
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect('\0%s' % name)
            s.send(message)
            return True
        except ConnectionRefusedError:
            return False

    @staticmethod
    def wait(name):
        """
        Wait until a mutex is released.

        :param name: The name of the mutex to wait on.
        :type name: string
        :raises: OSError -- when a problem occurs with the mutex socket.
        """
        while True:
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.bind('\0%s' % name)
                s.close()
                return
            except OSError as error:
                if not error.errno == errno.EADDRINUSE:
                    raise
            time.sleep(1)
