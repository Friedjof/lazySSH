from cmd import Cmd

from src.client import Client
from src.logging import logger


class Shell(Cmd):
    # Message to be output when cmdloop() is called.
    intro = None
    # Instead of using input(), this will use stdout.write() and stdin.readline(),
    # this means we can use any TextIO instead of just sys.stdin and sys.stdout.
    use_rawinput = False

    # Constructor that will allow us to set out own stdin and stdout.
    # If stdin or stdout is None, sys.stdin or sys.stdout will be used
    def __init__(self, client: Client, stdin=None, stdout=None):
        # call the base constructor of cmd.Cmd, with our own stdin and stdout
        super(Shell, self).__init__(completekey='tab', stdin=stdin, stdout=stdout)
        self.client = client

        # The prompt property can be overridden, allowing us to use a custom
        # string to be displayed at the beginning of each line. This will not
        # be included in any input that we get.
        self.prompt = f'{self.client.username}@{self.client.host}> '

        logger.info(f'User {self.client.username} connected from {self.client.host}:{self.client.port}')

    # These are custom print() functions that will let us utilize the given stdout.
    def print(self, value):
        # make sure the stdout is set.
        # we could add an else which uses the default print(), but I will not
        if self.stdout and not self.stdout.closed:
            self.stdout.write("\r" + value)

    def printline(self, value):
        self.print(value + '\n\r')

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        logger.info(f'User {self.client.username} inputted "{line.encode()}"')
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    # To create a command that is executable in our shell, we create functions
    # that are prefixed with do_ and contains the argument arg.
    # For example, if we want the command 'greet', we create do_greet().
    # If we want greet to take a name as well, we pass it as an arg.
    def do_greet(self, arg):
        if arg:
            self.printline('Hey {0}! Nice to see you!'.format(arg))
        else:
            self.printline('Hello there!')

    # even if you don't use the arg parameter, it must be included.
    def do_bye(self, arg):
        self.printline('See you later!')

        # if a command returns True, the cmdloop() will stop.
        # this acts like disconnecting from the shell.
        return True

    def do_clear(self, arg):
        self.print('\033c')

    # If an empty line is given as input, we just print out a newline.
    # This fixes a display issue when spamming enter.
    def emptyline(self):
        self.print('\r\n')

    def default(self, line: str) -> None:
        logger.info(f'User {self.client.username} tried to execute command "{line}"')
        self.printline(self.prompt)
        self.printline(f'Command "{line}" not found')
