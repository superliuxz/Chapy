#!/usr/bin/expect -f

set alias [lindex $argv 0]

spawn python3 ./client.py

expect "Please enter your alias:"

send "$alias\n"

interact

exit
