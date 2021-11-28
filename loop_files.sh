#!/bin/bash

for FILE in inputSequences/*.lms

do
  FILE_BASENAME=$(basename "$FILE")
  echo python3 convert.py \"$FILE_BASENAME\" \"$1\"
  python3 convert.py "$FILE_BASENAME" "$1"
  echo \"$FILE_BASENAME\" converted to the order of \"$1\"
done
