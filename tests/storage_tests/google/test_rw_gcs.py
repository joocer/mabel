import shutil
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], "../../.."))
from mabel.adapters.google import GoogleCloudStorageWriter, GoogleCloudStorageReader
from mabel.data.internals.dictset import STORAGE_CLASS
from mabel.data import BatchWriter
from mabel.data import Reader
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from rich import traceback

traceback.install()

BUCKET_NAME = "pytest"


def set_up():
    shutil.rmtree(".cloudstorage", ignore_errors=True)

    os.environ["STORAGE_EMULATOR_HOST"] = "http://localhost:9090"

    client = storage.Client(
        credentials=AnonymousCredentials(),
        project="testing",
    )
    bucket = client.bucket(BUCKET_NAME)
    try:
        bucket.delete(force=True)
    except:  # pragma: no cover
        pass
    bucket = client.create_bucket(BUCKET_NAME)


def test_gcs_binary():
    # set up
    set_up()

    w = BatchWriter(
        inner_writer=GoogleCloudStorageWriter,
        project="testing",
        blob_size=1024,
        dataset=f"{BUCKET_NAME}/test/gcs/dataset/binary",
        schema=["index"],
    )
    for i in range(200):
        w.append({"index": i + 300})
    w.finalize()

    # read the files we've just written, we should be able to
    # read over both paritions.
    r = Reader(
        inner_reader=GoogleCloudStorageReader,
        project="testing",
        dataset=f"{BUCKET_NAME}/test/gcs/dataset/binary",
        persistence=STORAGE_CLASS.MEMORY,
    )

    assert r.count() == 200, r.count()


def test_gcs_text():
    # set up
    set_up()

    w = BatchWriter(
        inner_writer=GoogleCloudStorageWriter,
        project="testing",
        blob_size=1024,
        format="jsonl",
        dataset=f"{BUCKET_NAME}/test/gcs/dataset/text",
        schema=["index"],
    )
    for i in range(250):
        w.append({"index": i + 300})
    w.finalize()

    # read the files we've just written, we should be able to
    # read over both paritions.
    r = Reader(
        inner_reader=GoogleCloudStorageReader,
        project="testing",
        dataset=f"{BUCKET_NAME}/test/gcs/dataset/text",
        persistence=STORAGE_CLASS.MEMORY,
    )

    assert r.count() == 250, r


if __name__ == "__main__":  # pragma: no cover
    from tests.helpers.runner import run_tests

    run_tests()
