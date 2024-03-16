"""
Test the file reader
"""

import datetime
import pytest
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], "../../.."))
from mabel.adapters.disk import DiskReader, DiskWriter
from mabel.data import Reader, BatchWriter
from mabel.errors import DataNotFoundError
from rich import traceback

traceback.install()


def test_can_find_files():
    def _inner(p):
        """
        ensure we can find the test files
        the test folder has two files in it
        """
        # with a trailing /
        r = DiskReader(dataset=p, raw_path=True)
        assert len(list(r.get_list_of_blobs())) == 2  # 2 data, 2 index

        # without a trailing /
        r = DiskReader(dataset=p, raw_path=True)
        assert len(list(r.get_list_of_blobs())) == 2  # 2 data, 2 index

    _inner("tests/data/tweets/")
    _inner(os.getcwd() + "/tests/data/tweets/")


def test_can_read_files():
    def _inner(p):
        """ensure we can read the test files"""
        r = DiskReader(dataset=p, raw_path=True)
        for file in [b for b in r.get_list_of_blobs() if "/_SYS." not in b]:
            for index, item in enumerate(r.get_blob_bytes(file).splitlines()):
                pass
            assert index == 24, index

    _inner("tests/data/tweets/")
    _inner(os.getcwd() + "/tests/data/tweets/")


def test_freshness_limits():
    def _inner(p, pt):
        # step back through time
        r = Reader(
            inner_reader=DiskReader,
            dataset=p,
            partitions=pt,
            start_date=datetime.date(2021, 1, 1),
            end_date=datetime.date(2021, 1, 1),
            freshness_limit="30d",
        )
        assert len(list(r)) == 50

    _inner("tests/data/dated/", ["{yyyy}-{mm}-{dd}"])
    _inner(os.getcwd() + "/tests/data/dated/", ["{yyyy}-{mm}-{dd}"])


def test_step_past():
    def _inner(p, pt):
        # step back through time
        r = Reader(
            inner_reader=DiskReader,
            dataset=p,
            partitions=pt,
            start_date=datetime.date(2021, 1, 1),
            end_date=datetime.date(2021, 1, 1),
            freshness_limit="5d",
        )
        with pytest.raises(DataNotFoundError):
            assert len(list(r)) == 0

    _inner("tests/data/dated/", ["{yyyy}-{mm}-{dd}"])
    _inner(os.getcwd() + "/tests/data/dated/", ["{yyyy}-{mm}-{dd}"])


def test_disk_binary():
    try:
        w = BatchWriter(
            inner_writer=DiskWriter,
            blob_size=1024,
            dataset=f"_temp/test/disk/dataset/binary",
            schema=["index"],
        )
        for i in range(200):
            w.append({"index": i + 300})
        w.finalize()

        # read the files we've just written, we should be able to
        # read over both paritions.
        r = Reader(
            inner_reader=DiskReader,
            dataset=f"_temp/test/disk/dataset/binary",
        )
        l = list(r)

        assert len(l) == 200, len(l)
    except Exception as e:  # pragma: no cover
        raise e


def test_disk_text():
    try:
        w = BatchWriter(
            inner_writer=DiskWriter,
            blob_size=1024,
            format="jsonl",
            dataset=f"_temp/test/gcs/dataset/text",
            schema=["index"],
        )
        for i in range(250):
            w.append({"index": i + 300})
        w.finalize()

        # read the files we've just written, we should be able to
        # read over both paritions.
        r = Reader(
            inner_reader=DiskReader,
            dataset=f"_temp/test/gcs/dataset/text",
        )
        l = list(r)

        assert len(l) == 250, len(l)
    except Exception as e:  # pragma: no cover
        raise e


if __name__ == "__main__":  # pragma: no cover
    from tests.helpers.runner import run_tests

    run_tests()
