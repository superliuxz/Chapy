#!/bin/bash

for i in {1..10000};
do
	xfce4-terminal -e "./run.sh $i"

done	
