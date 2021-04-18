import threading
import tempfile
import os
import io
from typing import Any
from ...formats.json import serialize
from ....logging import get_logger
from ....index import BTree

BLOB_SIZE = 32*1024*1024  # about 32 files per gigabyte
BUFFER_SIZE = BLOB_SIZE   # buffer in memory really
SUPPORTED_FORMATS_ALGORITHMS = ('jsonl', 'lzma', 'zstd', 'parquet')

class BlobWriter():

    def __init__(
            self,
            *,    # force params to be named
            inner_writer = None,  # type:ignore
            blob_size: int = BLOB_SIZE,
            format: str = 'zstd',
            **kwargs):

        self.format = format
        self.maximum_blob_size = blob_size

        if format not in SUPPORTED_FORMATS_ALGORITHMS:
            raise ValueError(F'Invalid format `{format}`, valid options are {SUPPORTED_FORMATS_ALGORITHMS}')

        kwargs['format'] = format
        self.inner_writer = inner_writer(**kwargs)  # type:ignore
        #self.index_on = kwargs.get('index_on', set())
        self._open_blob()


    def append(self, record: dict = {}):
        # serialize the record
        serialized = serialize(record, as_bytes=True) + b'\n'  # type:ignore

        # the newline isn't counted so add 1 to get the actual length
        # if this write would exceed the blob size, close it so another
        # blob will be created
        self.bytes_in_blob += len(serialized) + 1
        if self.bytes_in_blob > self.maximum_blob_size:
            self.commit()
            self._open_blob()

        # write the record to the file
        self.file.write(serialized)
        self.records_in_blob += 1

        #for field in self.index_on:
        #    self.indices[field].insert(record.get(field), self.records_in_blob)

        return self.records_in_blob

    def commit(self):

        #for field in self.index_on:
        #    print(self.indices[field].show())
        #get_logger().warning("TODO: indices aren't being saved")

        if self.bytes_in_blob > 0:
            with threading.Lock():
                try:
                    self.file.flush()
                    self.file.close()
                except ValueError:
                    pass

                if self.format == "parquet":
                    try:
                        from pyarrow import json as js  # type:ignore
                        import pyarrow.parquet as pq    # type:ignore
                    except ImportError as err:
                        get_logger().error("pyarrow must be installed to save as parquet")
                        raise err
                    
                    table = js.read_json(self.file_name)
                    pq.write_table(table, self.file_name + '.parquet', compression='ZSTD')
                    self.file_name += '.parquet'

                with open(self.file_name, 'rb') as f:
                    byte_data = f.read()
                    
                committed_blob_name = self.inner_writer.commit(
                        byte_data=byte_data,
                        override_blob_name=None)
                if 'BACKOUT' in committed_blob_name:
                    get_logger().warning(F"{self.records_in_blob:n} failed records written to BACKOUT partition {committed_blob_name}")
                get_logger().debug(F"Blob Committed - {committed_blob_name} - {self.records_in_blob:n} records, {self.bytes_in_blob:n} raw bytes, {len(byte_data):n} comitted bytes")
                try:
                    os.remove(self.file_name)
                except ValueError:
                    pass

                self.bytes_in_blob = 0
                self.file_name = None


    def _open_blob(self):
        self.file_name = self._create_temp_file_name()
        self.file: Any = open(self.file_name, mode='wb', buffering=BUFFER_SIZE)
        if self.format == 'lzma':
            import lzma
            self.file = lzma.open(self.file, mode='wb')
        if self.format == 'zstd':
            import zstandard  # type:ignore
            self.file = zstandard.open(self.file_name, mode='wb')

        self.bytes_in_blob = 0
        self.records_in_blob = 0
        #self.indices = {}
        #for field in self.index_on:
        #    self.indices[field] = BTree()

    def __del__(self):
        # this should never be relied on to save data
        self.commit()

    def _create_temp_file_name(self):
        """
        Create a tempfile, get the name and then deletes the tempfile.

        The behaviour of tempfiles is inconsistent between operating systems,
        this helps to ensure consistent behaviour.
        """
        file = tempfile.NamedTemporaryFile(prefix='mabel-', delete=True)
        file_name = file.name
        file.close()
        try:
            os.remove(file_name)
        except OSError:
            pass
        return file_name