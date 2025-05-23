#!/bin/bash

tools/make.exe $*
if [ $? -ne 0 ]; then
    read -p "Error building. Press any key to continue ..."
fi
