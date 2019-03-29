import sys, re

class TerminalController:
    """
    A class that can be used to portably generate formatted output to
    a terminal.

    `TerminalController` defines a set of instance variables whose
    values are initialized to the control sequence necessary to
    perform a given action.  These can be simply included in normal
    output to the terminal:

        >>> term = TerminalController()
        >>> print 'This is '+term.GREEN+'green'+term.NORMAL

    Alternatively, the `render()` method can used, which replaces
    '${action}' with the string required to perform 'action':

        >>> term = TerminalController()
        >>> print term.render('This is ${GREEN}green${NORMAL}')

    If the terminal doesn't support a given action, then the value of
    the corresponding instance variable will be set to ''.  As a
    result, the above code will still work on terminals that do not
    support color, except that their output will not be colored.
    Also, this means that you can test whether the terminal supports a
    given action by simply testing the truth value of the
    corresponding instance variable:

        >>> term = TerminalController()
        >>> if term.CLEAR_SCREEN:
        ...     print 'This terminal supports clearning the screen.'

    Finally, if the width and height of the terminal are known, then
    they will be stored in the `COLS` and `LINES` attributes.
    """
    BOL = ''
    UP = ''
    DOWN = ''
    LEFT = ''
    RIGHT = ''
    CLEAR_SCREEN = ''
    CLEAR_EOL = ''
    CLEAR_BOL = ''
    CLEAR_EOS = ''
    BOLD = ''
    BLINK = ''
    DIM = ''
    REVERSE = ''
    NORMAL = ''
    HIDE_CURSOR = ''
    SHOW_CURSOR = ''
    COLS = None
    LINES = None
    BLACK = BLUE = GREEN = CYAN = RED = MAGENTA = YELLOW = WHITE = ''
    BG_BLACK = BG_BLUE = BG_GREEN = BG_CYAN = ''
    BG_RED = BG_MAGENTA = BG_YELLOW = BG_WHITE = ''
    _STRING_CAPABILITIES = ('\n    BOL=cr UP=cuu1 DOWN=cud1 LEFT=cub1 RIGHT=cuf1\n    CLEAR_SCREEN=clear CLEAR_EOL=el CLEAR_BOL=el1 CLEAR_EOS=ed BOLD=bold\n    BLINK=blink DIM=dim REVERSE=rev UNDERLINE=smul NORMAL=sgr0\n    HIDE_CURSOR=cinvis SHOW_CURSOR=cnorm').split()
    _COLORS = ('BLACK BLUE GREEN CYAN RED MAGENTA YELLOW WHITE').split()

    def __init__(self, term_stream=sys.stdout):
        """
        Create a `TerminalController` and initialize its attributes
        with appropriate values for the current terminal.
        `term_stream` is the stream that will be used for terminal
        output; if this stream is not a tty, then the terminal is
        assumed to be a dumb terminal (i.e., have no capabilities).
        """
        try:
            import curses
        except:
            return
        else:
            if not term_stream.isatty():
                return
            try:
                curses.setupterm()
            except:
                return

            self.COLS = curses.tigetnum('cols')
            self.LINES = curses.tigetnum('lines')
            for capability in self._STRING_CAPABILITIES:
                attrib, cap_name = capability.split('=')
                setattr(self, attrib, self._tigetstr(cap_name) or '')

        set_fg = self._tigetstr('setf')
        if set_fg:
            for i, color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, color, curses.tparm(set_fg, i) or '')

        set_bg = self._tigetstr('setb')
        if set_bg:
            for i, color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, 'BG_' + color, curses.tparm(set_bg, i) or '')

    def _tigetstr(self, cap_name):
        import curses
        cap = curses.tigetstr(cap_name) or ''
        return re.sub('\\$<\\d+>[/*]?', '', cap)

    def render(self, template):
        """
        Replace each $-substitutions in the given template string with
        the corresponding terminal control string (if it's defined) or
        '' (if it's not).
        """
        return re.sub('\\$\\$|\\${\\w+}', self._render_sub, template)

    def _render_sub(self, match):
        s = match.group()
        if s == '$$':
            return s
        return getattr(self, s[2:-1])


class ProgressBar:
    """
    A 3-line progress bar, which looks like::

                                Header
        20% [===========----------------------------------]
                           progress message

    The progress bar is colored, if the terminal supports color
    output; and adjusts to the width of the terminal.
    """
    BAR = '%3d%% ${GREEN}[${BOLD}%s%s${NORMAL}${GREEN}]${NORMAL}\n'
    HEADER = '${BOLD}${CYAN}%s${NORMAL}\n\n'

    def __init__(self, term, header):
        self.term = term
        if not (self.term.CLEAR_EOL and self.term.UP and self.term.BOL):
            raise ValueError("Terminal isn't capable enough -- you should use a simpler progress dispaly.")
        self.width = self.term.COLS or 75
        self.bar = term.render(self.BAR)
        self.header = self.term.render(self.HEADER % header.center(self.width))
        self.cleared = 1
        self.update(0, '')

    def update(self, percent, message):
        if self.cleared:
            sys.stdout.write(self.header)
            self.cleared = 0
        n = int((self.width - 10) * percent)
        sys.stdout.write(self.term.BOL + self.term.UP + self.term.CLEAR_EOL + self.bar % (100 * percent, '=' * n, '-' * (self.width - 10 - n)) + self.term.CLEAR_EOL + message.center(self.width))

    def clear(self):
        if not self.cleared:
            sys.stdout.write(self.term.BOL + self.term.CLEAR_EOL + self.term.UP + self.term.CLEAR_EOL + self.term.UP + self.term.CLEAR_EOL)
            self.cleared = 1
