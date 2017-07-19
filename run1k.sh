#!/bin/bash

for i in {1..10000};
do
	gnome-terminal -e "./run.sh $i"

done	
