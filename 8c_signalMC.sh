#!/bin/bash
# This file just copies the signalMC to "signal_scaled" folder
path=$(pwd)

# Input Directory
input_path="$path/cs/test/prescale_combine"


# Create Output Directory to save combined root files
output_path="$path/cs/test/signal_scaled"
if [ -d "$output_path" ]
then
    echo "$output_path already exists."
else 
    $(mkdir -p ${output_path})
    echo "$output_path has been created"
fi

echo "$(cp $input_path/test_signal.root $output_path/test_signal.root)"
        #it's just copying a file from one folder to another folder with same name
echo "$output_path/test_signal.root has been created to be combined."