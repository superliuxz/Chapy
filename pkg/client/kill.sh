#!/bin/bash

for pid in $(ps aux | grep "python3 ./client" | awk '{print $2}');
do
	kill -9 $pid;
done

