import socket
import threading
import argparse
import logging.config

logging.config.fileConfig("logging.ini")
logger = logging.getLogger("root")


class Pipe(object):

    def __init__(self, source, target):
        self.source = source
        self.target = target

    def start(self):
        t = threading.Thread(target=self._run, )
        t.start()

    def _run(self):
        source = f"{self.source.getpeername()[0]}:{self.source.getpeername()[1]}"
        target = f"{self.target.getpeername()[0]}:{self.target.getpeername()[1]}"
        while True:
            buffer = self.source.recv(1024)
            if not buffer:
                logger.info(f"{source} -> {target} closed ")
                break
            logger.debug(buffer)
            self.target.send(buffer)


class Proxy(object):

    def __init__(self, lh, lp, th, tp):
        self.host = lh
        self.port = int(lp)
        self.t_host = th
        self.t_port = int(tp)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server.bind((self.host, self.port), )
        except TypeError:
            logger.error("监听地址格式有误")
            return

        self.server.listen(1024)
        logger.info(f"Listen on {self.host}:{self.port} ...")

        while True:
            source, addr = self.server.accept()
            logger.info(f"Accept Client on {addr[0]}:{addr[1]}")
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.connect((self.t_host, self.t_port))

            Pipe(source, target).start()
            Pipe(target, source).start()


def parse_args():
    parser = argparse.ArgumentParser(description="TCP Proxy in Python")
    parser.add_argument("-s", help="Proxy Sever Listen Address", required=True)
    parser.add_argument("-t", help="Target Server Listen Address", required=True)
    parser.add_argument("--log", help="Set log level  (debug|info|warning|error)")
    return parser.parse_args()


def set_log_level(level):
    level = level.log
    if level:
        if "info" in level:
            logger.setLevel(logging.INFO)
        elif "warning" in level:
            logger.setLevel(logging.WARNING)
        elif "error" in level:
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    args = parse_args()

    set_log_level(args)

    l_host, l_port = args.s.split(":")
    t_host, t_port = args.t.split(":")
    Proxy(l_host, l_port, t_host, t_port).run()
