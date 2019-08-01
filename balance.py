import os
import sys
from urllib.parse import urlparse

from pyshard import Pyshard
from sync import Client

import settings

pid = os.getpid()


def _main_loop(db: Pyshard, sync: Client):
    for line in sys.stdin:
        url = line.rstrip()
        index, key = _parse_url(url)
        exists, hash_ = db.has(index, key)
        # TODO: index config (default index)
        if exists:
            continue
        if not sync.acquire_no_wait(hash_):
            continue
        sys.stdout.write(f'pid={pid}: {url}\n')
        sys.stdout.flush()


def _parse_url(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc, parsed_uri.path


def main():
    db = Pyshard(('localhost', 9192))
    with Client(settings.SERVER_ADDR) as sync:
        _main_loop(db, sync)


if __name__ == "__main__":
    main()
