#!/usr/bin/env bash
valgrind --leak-check=yes --log-file=$1 --suppressions=valgrind-python.supp python ./isk-daemon.py
