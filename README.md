# KB File Comparison to ProcMon

This is a small project that is a one-off to research some
strange behavior seen with Google Chrome that seemed to be 
tied to a particular patch.

This code works in two parts.  First, a list of KBs and URLs that
point to their file list are required.
1. Find the KB in the catalog (https://www.catalog.update.microsoft.com/)
2. In the Update Details for the KB, go to the More Information link
3. In the More Information page, locate the link for "file information"
   and save that into the csv. Use these columns: 
   kb,title,file_list_uri
4. Run the `all_kb_files.csv kb_file_urls.csv` where the second parameter
   is the CSV file you just created.
5. Redirect output to a file of your choice, like `all_kb_files.csv`

Second, use ProcMon, from SysInternals, in Windows to create a 
list of files opened in the test scenario.  Filter out as many 
external programs as possible.
A sample `.PMC` file is provided that:
* Only shows file activity
* Filters out file query requests (information, permission)
* Shows only successful activity, to squish attempts to find a file
* Filters out programs running before the test

If these filters aren't in place, the output will be extra noisy.
A sample run of installing Chrome on Windows 10 is provided for testing.

1. Start ProcMon
2. Filter out events as described above
3. Clear the output
4. Conduct the test
5. Stop collection in ProcMon
6. Save the output as CSV for all events as filtered.  Recommended names
   should include date, time, program, or test run ID if you've got a test plan.
7. Copy the CSV to the system with this archive, if they are on separate 
   systens.
8. Run `compare-procmon-kb-files.py` with two parameters, the ProcMon CSV
   and the `all_kb_files.csv` from the first phase.
9. Output will go on stdout with every executable and KBs that impacted them. 
   Save to another file if desired.
10. Review the output and look for your main executable.
11. For every focus exe (e.g. `chrome.exe`), rerun the
    compare script with a third parameter of the executable name.
    e.g. `compare-procmon-kb-files.py 20230315-preocmon-chrome-install-run.csv all_kb_files.csv chrome.exe`
12. The output now shows specific files from specific KBs that
    came from changes made by a specific KB.

## Sample report excerpt - two parameters
```txt
ChromeSetup.exe used files updated by these KBs:
  - KB5018411
GoogleUpdate.exe used files updated by these KBs:
  - KB5021654
  - KB5018411
  - KB5020439
  - KB5022289
  - KB5022838
  - KB5021235
  - KB5019964
consent.exe used files updated by these KBs:
  - KB5021654
  - KB5018411
  - KB5020439
```

## Sample report excerpt - three parameters (focus exe)
```txt
chrome.exe used files updated by these KBs:
  - KB5021235
    - wtsapi32.dll
    - winmm.dll
    - version.dll
  - KB5022838
    - wtsapi32.dll
    - winmm.dll
    - version.dll
  - KB5018411
    - clbcatq.dll
    - msmpeg2vdec.dll
    - SHCore.dll
    - dlnashext.dll
    - twinapi.appcore.dll
    - cscui.dll
    - usermgrcli.dll
```