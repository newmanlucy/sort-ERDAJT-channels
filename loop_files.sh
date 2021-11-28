#!/bin/bash

for FILE in inputSequences/*.lms
do
  FILE_BASENAME=$(basename "$FILE")
  echo python3 convert.py "$@" \"$FILE_BASENAME\"
  python3 convert.py "$@" "$FILE_BASENAME"
  echo \"$FILE_BASENAME\" converted
done
