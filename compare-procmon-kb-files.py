#!/usr/bin/env python
import sys
import csv


def usage():
    print(f'Usage: {sys.argv[0]} [procmon_csv] [kb_csv]')
    print('Purpose: Search procmon output for files modified in select')
    print('         KBs.  When found, the KB and file are listed.')
    print('procmon_csv - export of files from SysInternals ProcMon tool')
    print('         See the associated PMC for how to configure the tool.')
    print('kb_csv - output of running get_kb_filelist.py kb_file_urls.csv')
    print('         and contains just "kb,path" on the first line.')
    exit(1)


try:
    procmon_fd = open(sys.argv[1], 'r')
    procmon_csv = csv.DictReader(procmon_fd, dialect='excel')
    kb_fd = open(sys.argv[2], 'r')
    kb_csv = csv.DictReader(kb_fd)
except BaseException as e:
    print("Missing required parameters or there were errors parsing the CSV")
    print(str(e))
    usage()

def kb_csv_to_dict(table):
    out = dict()
    for row in table:
        kb = row.get('kb')
        path = row.get('path')
        if path in out and kb not in out[path]:
            out[path].append(kb)
        else:
            out[path] = [kb]
    return out

try:
    kb_dict = kb_csv_to_dict(kb_csv)
    del kb_csv
    kb_fd.close()
except BaseException as e:
    print('There was a failure parsing the KB CSV file.  Columns are kb,path.')
    print(str(e))
    exit(1)

print('process,path,operation,kb_list')
paths_shown = set()
for row in procmon_csv:
    op = row.get('Operation')
    full_path = row.get('Path')
    process_name = row.get('Process Name')
    success = row.get('Result') == "SUCCESS"
    if success and op and full_path and str(op).find('File') >= 0:
        short_path = str(full_path).split('\\')[-1]
        if short_path and short_path in kb_dict and short_path not in paths_shown:
            paths_shown.add(short_path)
            print(f'"{process_name}",{short_path},{op},"{kb_dict[short_path]}"')

procmon_fd.close()