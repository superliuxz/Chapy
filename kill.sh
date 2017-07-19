#!/bin/bash

for pid in $(ps aux | grep "python3 ./seng299" | awk '{print $2}');
do
	kill -9 $pid;
done

