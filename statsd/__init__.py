import sys

from .client import StatsClient, TCPStatsClient, UnixSocketStatsClient

if sys.version_info >= (3, 8):  # pragma: >=3.8 cover
    import importlib.metadata as importlib_metadata
else:  # pragma: <3.8 cover
    import importlib_metadata

__version__ = version = importlib_metadata.version(__name__)
__all__ = ["StatsClient", "TCPStatsClient", "UnixSocketStatsClient"]
