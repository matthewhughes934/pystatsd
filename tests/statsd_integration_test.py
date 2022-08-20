from __future__ import annotations

import itertools
import random
import socket
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import TypeVar
from unittest import mock

import pytest

from statsd import StatsClient, TCPStatsClient, UnixSocketStatsClient
from statsd.client.base import StatsClientBase

TERMINATOR = "end-of-test"
# Start from a random point each time
# to avoid quickly repeat runs  failing due to
# "port already in use"
PORT_POOL = itertools.count(random.randint(1024, 65_535))


@pytest.fixture
def port() -> int:
    return next(PORT_POOL)


Client = TypeVar("Client", bound=StatsClientBase)


@contextmanager
def terminating_client(client: Client) -> Generator[Client, None, None]:
    try:
        yield client
    finally:
        client._send(TERMINATOR)


class UDPServer(threading.Thread):
    def __init__(
        self,
        sock: socket.socket,
        addr: tuple[str, int],
    ) -> None:
        self._sock = sock
        self._addr = addr
        self.received: list[str] = []
        self.listening = False

        super().__init__()

    def run(self) -> None:
        with self._sock as sock:
            sock.bind(self._addr)
            self.listening = True

            while True:
                raw_data, _ = sock.recvfrom(1024)
                data = raw_data.decode()

                if TERMINATOR in data:
                    break
                else:
                    self.received.append(data)


class StreamServer(threading.Thread):
    def __init__(self, sock: socket.socket, addr: tuple[str, int] | str) -> None:
        self._sock = sock
        self._addr = addr
        self.received: list[str] = []
        self.listening = False

        super().__init__()

    def run(self) -> None:
        with self._sock as sock:
            sock.bind(self._addr)
            sock.listen()
            self.listening = True

            conn, _ = sock.accept()
            with conn:
                keep_going = True
                while keep_going:
                    data = conn.recv(1024).decode()

                    for line in data.splitlines():
                        if line == TERMINATOR:
                            keep_going = False
                            break
                        else:
                            self.received.append(line)


@pytest.fixture
def udp_pair(port):
    host = "localhost"
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return (StatsClient(host=host, port=port), UDPServer(server_socket, (host, port)))


@pytest.fixture
def tcp_pair(port):
    host = "localhost"
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return (TCPStatsClient(host, port), StreamServer(server_socket, (host, port)))


@pytest.fixture
def unix_pair(tmpdir):
    if not hasattr(socket, "AF_UNIX"):
        pytest.skip("Skipping: Unix sockets not supported")
    path = str(tmpdir / "test_socket")
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    return (UnixSocketStatsClient(path), StreamServer(server_socket, path))


@pytest.fixture(params=("udp_pair", "tcp_pair", "unix_pair"))
def client_server_pair(request):
    return request.getfixturevalue(request.param)


@mock.patch.object(random, "random", lambda: -1)
def test_incr(client_server_pair):
    client, server = client_server_pair
    server.start()

    while not server.listening:
        time.sleep(0.01)

    with terminating_client(client):
        client.incr("foo")
        client.incr("foo", 10)
        client.incr("foo", 10, rate=0.5)

    client.close()
    server.join()

    assert server.received == ["foo:1|c", "foo:10|c", "foo:10|c|@0.5"]


@mock.patch.object(random, "random", lambda: -1)
def test_decr(client_server_pair):
    client, server = client_server_pair
    server.start()

    while not server.listening:
        time.sleep(0.01)

    with terminating_client(client):
        client.decr("foo")
        client.decr("foo", 10)
        client.decr("foo", 10, rate=0.5)

    client.close()
    server.join()

    assert server.received == ["foo:-1|c", "foo:-10|c", "foo:-10|c|@0.5"]


@mock.patch.object(random, "random", lambda: -1)
def test_guage(client_server_pair):
    client, server = client_server_pair
    server.start()

    while not server.listening:
        time.sleep(0.01)

    with terminating_client(client):
        client.gauge("foo", 30)
        client.gauge("foo", 1.2)
        client.gauge("foo", 70, rate=0.5)

    client.close()
    server.join()

    assert server.received == ["foo:30|g", "foo:1.2|g", "foo:70|g|@0.5"]
