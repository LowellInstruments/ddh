# Changelog

1.0.02

    some API functions crashing due to "master" branch renamed

1.0.03

    added API controller process

1.0.04 - October 23, 2024

    fixed function api_get_fw_cell_version() readlines index

1.0.05 - November 7, 2024

    fixed function api_read_aws_sqs_ts()


1.0.06 - November 12, 2024

    api_get_api_version() based on .api_version file
    /info endpoint now returns free disk space

1.0.07 - February 10, 2025

    ep_history we added a "since" parameter

1.0.08 - February 18, 2025

    make ep_history compare against local time not UTC

1.0.10 - March 13, 2025

    added DWService start / stop endpoints

1.0.11 - 05/08/2025

    Added network interfaces fields on INFO endpoint
    Changed this CHANGELOG.md file date format.

1.0.12 - 06/06/25

    added API method ep_logs_get_with_since()

1.0.13 - 07/01/25

    added aws_grouped() in INFO endpoint, returns 1 if AWS grouped
