import paramiko

from src.client import Client
from src.logging import logger


class SshServerInterface(paramiko.ServerInterface):
    # This will allow the SSH server to provide a
    # channel for the client to communicate over.
    # By default, this will return OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED,
    # so  we have to override it to return OPEN_SUCCEEDED 
    # when the kind of channel requested is "session".
    def __init__(self, client: Client):
        super(SshServerInterface, self).__init__()
        self.client = client
        self.true = None

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    # AFAIK, pty (pseudo-tty (TeleTYpewriter)) will allow our
    # client to interact with our shell.
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        self.true = True
        return self.true

    # This allows us to provide the channel with a shell we can connect to it.
    def check_channel_shell_request(self, channel):
        return True

    # This let's us setup password authentication.
    # There are better ways to do this than using plain text,
    # but for ease of development for me and this tutorial
    # I think plain text is acceptable.
    #
    # For posterity, you could setup a database that encrypts
    # passwords and will grab them to decrypt here.
    def check_auth_password(self, username, password):
        self.client.username = username
        self.client.password = password

        if (username == 'admin') and (password == 'password'):
            logger.info(f'User {username} authenticated successfully')
            return paramiko.AUTH_SUCCESSFUL

        logger.info(f'User {username} failed to authenticate')
        return paramiko.AUTH_FAILED

    # String that will display when a client connects,
    # before authentication has happened. This is different
    # than the shell's intro property, which is displayed 
    # after the authentication.
    def get_banner(self):
        return 'My SSH Server\r\n', 'en-US'
