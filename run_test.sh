#!/usr/bin/env bash


trap "echo trap; exit" SIGINT SIGTERM ERR EXIT
ls /tmp2/caca

echo 1
echo 2
