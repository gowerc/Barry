
file=$1
fileext=${file##*.}
rootname=$(basename $file .$fileext)
dirloc=$(dirname $file)
PYTHON=/home/pi/Barry/venv/bin/python

$PYTHON  $file   >  ${dirloc%scripts}logs/${rootname}-$(date +\%Y-\%m-\%d).log  2>&1

