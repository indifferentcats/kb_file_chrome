#!/usr/bin/env python
import sys
import csv
import logging
from io import StringIO
from pathlib import Path
from typing import Union
import urllib.parse
import urllib.request

output_file = "all_kb_files.csv"
logging.basicConfig(level=logging.DEBUG)

fd = sys.stdin
if len(sys.argv) >= 2:
    logging.debug("Command line argument discovered")
    file_name = sys.argv[1]
    logging.debug(f"Opening input file {file_name}")
    if file_name and Path(file_name).is_file():
        fd = open(file_name, "r")
    else:
        logging.warning(f"No such input file {file_name}")
        exit(1)
else:
    logging.info("Reading CSV from stdin")

# hints from https://stackoverflow.com/questions/47741235/how-to-read-bytes-object-from-csv
def get_uri_content_stringio(uri, skip_first=True) -> Union[StringIO, None]:
    response = urllib.request.urlopen(uri)
    if response.status >= 400:
        logging.warning(f'Error retrieving URI {uri} for {kb}')
        return None
    if skip_first:
        description = response.fp.readline()
    lines = [line.decode('utf-8') for line in response.readlines()]
    return StringIO("".join(lines))


kb_csv = csv.DictReader(fd)
logging.info(f"Creating output CSV {output_file}")
with open(output_file, 'w', newline='') as csvwriter:
    all_kb_files = csv.DictWriter(csvwriter,
                                  fieldnames=["kb",
                                              "path",
                                              "base_path"],
                                  dialect='excel')
    all_kb_files.writeheader()
    for row in kb_csv:
        if not row.get('file_list_uri'):
            raise KeyError("Input CSV is missing file_list_uri column")
        kb = row['kb']
        logging.info(f'Getting file list for KB {kb}')
        uri = row['file_list_uri']
        logging.debug(f'Requesting URI {uri}')
        sio_fd = get_uri_content_stringio(uri)
        if sio_fd:
            kb_file_list = csv.DictReader(sio_fd)
            for record in kb_file_list:
                file_name = record.get('File name')
                output_row = {
                    "kb": kb,
                    "path": file_name,
                    "base_path": Path(file_name).parts[-1]
                }
                all_kb_files.writerow(output_row)

fd.close()
