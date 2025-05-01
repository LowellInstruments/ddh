# Changelog

4.0.00

    2024 version of the DDH App

4.0.01 

    fixed in_ports_geo.py detection

4.0.02

    added notification field 'dl_files'

4.0.03

    added removal of mobile GPS JSON files older than 2 days

4.0.04

    bug in logs.py in building file_out on testing mode

4.0.05
    
    prevented deletion of error_maps.gif when receiving doppio maps from DDN
    added possibility of water column mode for TDO

4.0.06

    added fix for summary box DO-1 / DO-2

4.0.07

    added water column mode for graphing for DOX and TDO loggers
    added new logs.py entries, with unified timestamp
    added year filtering on AWS uploads

4.0.08

    added new maps GOM / MAB
    fixed bug setup_tab not opening after pressing "cancel without saving"
    cleaned logs generation
    made the graphs show the same order than the history

4.0.09

    Some things were not plotted for LI loggers, re-arranged water column mode

4.0.10

    Fixed command DEL using wrong filename when "testmode_" is ON.

4.0.11

    Added BRT tool to DDC and BRT compiled binary to DDH distribution.

4.0.12

    Got rid of redundant configuration file .ts_aws.txt

4.0.13

    Added fast mode for TDO loggers.
    Added new "orange tick" icon for when we do NOT rerun the logger.
    maps GIFs to .gitignore
    pop_ddh2.sh -> pop_ddh.sh

4.0.14

    fixed notification GPS error from Nick
    https://app.asana.com/0/1206361785539879/1208148157218367/f
    rearranged a bit main_gui and utils_gui.py

4.0.15

    added, and disabled, AWS_CP after each logger download
    for Lowell loggers, added scaled BAT measurement via factor

4.0.16

    improved script_ddc

4.0.17

    added notification number of GPS satellites
    modified test GPS duration from 30 -> 60 seconds
    added a condition to ignore filenames containing 'testfile_' in CST

4.0.18

    made number of satellites notification only run on "Maggie Sue"

4.0.19

    added auto detection of USB ports for Quectel shield

4.0.20

    fixed an issue with new DDH GUI watchdog

4.0.21 - September 16, 2024

    fixed checkbox value plt_outside_water
    do not plot testfile_ files

4.0.22 - September 18, 2024

    added new BLE library for DOX / TDO and [experimental] section
    script_ddc now detecting properly cell internet on issues 'i'

4.0.23 - September 19, 2024

    fixed some bug in BLE_LSB_DOX
    added notification when cannot clock sync at boot

4.0.24 - September 23, 2024

    fixed logic bug plot-in-water, out-of-water

4.0.25 - September 25, 2024

    improved code readability on DDH, not MAT

4.0.26 - September 25, 2024

    had to add _lock_icon(0) on utils_gui, STATE_DDS_BLE_HARDWARE_ERROR

4.0.27 - September 26, 2024

    new strategy to not send so many BLE hardware errors via e-mail
    disabled CRC on TDO logger downloads per default

4.0.28 - September 27, 2024

    done better CST, less logs

4.0.29 - October 1, 2024

    reduced printed logs a lot
    added some direct SNS alarm notifications (no SQS) to API if this crashes
    added API controller process to API

4.0.30 - October 3, 2024

    graphing ALL data is the new default, before it was only IN-WATER data

4.0.31 - October 7, 2024

    forcing AWS sync even if number of files = 0 so API is refreshed
    better obtaining ICCID when executing run_dds.sh

4.0.32 - October 16, 2024

    dynamic reconfiguration TDO / DOX on config.toml experimental conf_tdo and conf_dox

4.0.33 - October 20, 2024

    slightly better main_controller_api

4.0.34 - October 22, 2024

    added error when no plotting because only testfiles_ are present

4.0.35 - November 12, 2024

    new buttons strategy in file dds/buttons.py

4.0.36 - November 14, 2024

    improved buttons strategy in file dds/buttons.py
    improved AWS cp vs sync
    added better condition on DO2 when changing DRI

4.0.37 - November 14, 2024

    removed the e) edit BLE range tool option from DDC

4.0.38 - November 15, 2024

    moved GPQ file generation to generate smaller files

4.0.39 - November 16, 2024

    disabled CST_serve in main_dds.py

4.0.40 - November 16, 2024

    DOX loggers, better logic for "need for DOX interval reconfiguration"

4.0.41 - November 16, 2024

    improved GPQ file generation to remove warning

4.0.42 - November 18, 2024

    DDC new checks it can connect to AWS
    bug: AWS_CP better cloud icon update, it stayed just "busy"

4.0.43 - November 18, 2024

    better ways to detect process running

4.0.44 - November 22, 2024

    hardcoded DHU="00050" in TDO deploy script

4.0.45 - November 24, 2024

    new LOCAL API main_dda for features such as smart lock out time

4.0.46 - December 8, 2024

    moved SCC 00050 in script_deploy_logger_tdo_utils.py

4.0.47 - December 9, 2024

    removed checkbox plot only water and it is now the default

4.0.48 - December 9, 2024

    cleaned a bit the code for graphing

4.0.49 January 8, 2025

    Bluetooth Range Tool (BRT) now orders dropdown by descending serial number
    GPS label on history tab shows now less digits
    Added numbers of the rows in history table

4.0.50 January 9, 2025

    added warning string on graphs 'all data is out-of-water'

4.0.51 January 9, 2025

    selection of SCF file to deploy to loggers automatically by DDH on "Advanced" tab

4.0.52 January 10, 2025

    added feature: smart-lock-out

4.0.53 January 15, 2025

    added feature: map trawls

4.0.54 January 17, 2025

    added feature: AWS copy instead of AWS sync

4.0.55 January 17, 2025

    added feature: merged GPS3 branch

4.0.56 January 21, 2025

    added featured: fixed GPS3 merged branch with minor conditions

4.0.57 January 22, 2025

    Addressed Huanxin request for feature: save DDH screen brightness value between runs

4.0.58 January 22, 2025

    Added GPS still waiting icon

4.0.59 January 22, 2025

    Bug fix: removed MAT library _emit_conversion_progress, seemed too stressful for GUI

4.0.60 January 22, 2025

    When error, data in plot is not displayed

4.0.61 January 24, 2025

    DDC button tests should be fixed

4.0.62 January 24, 2025

    Better way to report GPS sync at boot error

4.0.63 January 24, 2025

    Added a way to know if sixfab is installed

4.0.64 January 27, 2025

    Added the "happen" interface

4.0.65 January 30, 2025

    Simplified Smart-Lock-Out feature
    Simplified GPS error e-mail notifications

4.0.66 February 4, 2025

    Added GPS signal quality to DCC

4.0.67 February 5, 2025

    Fixed bug in aws_sync_or_cp() with os.path.exists()

4.0.68 February 7, 2025

    Improved script GPS quality test

4.0.69 February 7, 2025

    Minimized SQS notifications around the port

4.0.70 February 10, 2025

    optimized logs size by removing some repeated lines in graphs size

4.0.71 February 11, 2025

    now DDC checks local DDH version vs github's one

4.0.72 February 14, 2025

    added DDC capability to detect ppp0 interfaces
    added DDC capatility to detect sixfab software running
    improved DDC explanation strings
    made DDC GPS signal quality test infinite

4.0.73 February 15, 2025

    changed "Maps" tab label to "Models"
    "Models" tab selection is sticky, so it is remembered between DDH runs

4.0.74 February 19, 2025

    added text input to filter and add loggers by serial number on "Setup" tab

4.0.75 February 21, 2025

    added new experimental flag 'exp_new_side_buttons'

4.0.76 February 21, 2025

    fixed continuously uploading same but growing track.txt to AWS S3
    fixed smart_lock_out when colored macs

4.0.77 February 24, 2025

    adjusted smart_lock_out condition

4.0.78 February 26, 2025

    improved switch wifi-to-cell-to-wifi condition

4.0.79 Febfruary 28, 2025

    skipped so 4.0.80 fixing a bug is easier to remember

4.0.80 February 28, 2025

    bug: super command DDH_B makes a logger crash
    solution: make DDH do not send super commands on lower version loggers
    bug: sometime does not detect BLE dead
    solution: created function linux_is_process_running_strict()

4.0.81 February 28, 2025

    removed bad code to force bug on aws

4.0.82 March 11, 2025

    changed buttons to work by default with new thread by setting new_or_old = 1 in buttons.py
    test #8 to create the release
    we now create releases with the following commands:
        git add -A
        git commit -m 'whatever'
        git tag v1234
        git push -u origin toml tag v1234
    DDT also changed

4.0.83 March 13, 2025

    bug: in some very weird case, JSON-SQS files cannot be decoded, fixed it

4.0.84 March 19, 2025

    simplified smart-lockout, this does not affect users because it is still an experimental flag

4.0.85 March 20, 2025

    now the lowest side button sets screen brightness to 0
    you can use the highest side button to set it back to >0 values

4.0.86 March 21, 2025

    DDC option 'g' now gives you more information and also resets at start
    smart lock-out feature is finished but disabled by default

4.0.87 March 24, 2025

    added retries to try to get the ICCID of the SIM card at beginning of run

4.0.88 March 25, 2025

    added possibility of not-available data on Summary box on DOX and TDO loggers

4.0.89 April 22, 2025

    updated /etc/ppp/options

4.0.90 April 29, 2025

    in MAT library file lix.py, added  
            # firmware patch, mm[i] should be pointing to sensor mask
            if mm[i] == 0:
                break
    makes file conversion more robust on application BIL, probably also on DDH

4.0.91 May 1, 2025

    fixed typo on file .ddh_version, it had a "cd" string on it

4.0.92 May 1, 2025

    I rolled back 4.0.90 which was wrong

4.0.93 May 1, 2025

     The patch on 4.0.90 was wrong, fixed it


