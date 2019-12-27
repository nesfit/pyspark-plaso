#!/bin/bash
DEST=../lib
if [ ! -d $DEST ]; then
    mkdir $DEST
fi
for I in `cat dependencies.txt`; do
    pip install --target=../lib $I
done
