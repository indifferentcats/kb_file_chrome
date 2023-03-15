#!/usr/bin/env python
import sys
import csv
from collections import namedtuple

def usage():
    print(f'Usage: {sys.argv[0]} [procmon_csv] [kb_csv] {{process_exe}}')
    print('Purpose: Search procmon output for files modified in select')
    print('         KBs.  When found, a report is shown of KBs which ')
    print('         impacted each executable in the trace.')
    print('procmon_csv - export of files from SysInternals ProcMon tool')
    print('         See the associated PMC for how to configure the tool.')
    print('kb_csv - output of running get_kb_filelist.py kb_file_urls.csv')
    print('         and contains just "kb,path" on the first line.')
    print('process_exe - if specified, and if it matches on of the processes,')
    print('         the list of files and their respective KBs is also shown')
    exit(1)


focus_exe = None
if len(sys.argv) == 4:
    focus_exe = str(sys.argv[3])

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

ProgReport = namedtuple("ProgReport", "kb_set file_set")
report_data = dict()
for row in procmon_csv:
    op = row.get('Operation')
    full_path = row.get('Path')
    process_name = row.get('Process Name')
    success = row.get('Result') == "SUCCESS"
    if success and op and full_path and str(op).find('File') >= 0:
        short_path = str(full_path).split('\\')[-1]
        if short_path and short_path in kb_dict:
            if process_name not in report_data:
                report_data[process_name] = ProgReport(set(kb_dict[short_path]),set([short_path]))
            else:
                for kb in kb_dict[short_path]:
                    report_data[process_name].kb_set.add(kb)
                report_data[process_name].file_set.add(short_path)

for proc in report_data:
    if not focus_exe:
        print(f'{proc} used files updated by these KBs:')
        [print(f'  - {x}') for x in report_data[proc].kb_set]
    elif focus_exe == proc:
        # output is "  - KB5012345"
        #           "      - app.dll"
        print(f'{proc} used files updated by these KBs:')
        for kb in report_data[proc].kb_set:
            print(f'  - {kb}')
            for one_file in report_data[proc].file_set:
                if kb in kb_dict[one_file]:
                    print(f'    - {one_file}')
    # else:
    #     print(f'Skipping {proc} as it is not the focus of this report')
procmon_fd.close()