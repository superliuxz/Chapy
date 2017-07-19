#!/bin/bash

for i in {1..1000};
do
	gnome-terminal -e "./run.sh $i"

done	