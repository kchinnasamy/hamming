echo "Testing hamming.py"
# Get arg count
if [ $# -ne 1 ]; then
    echo "usage: bash test_hamming.sh [asc|bin]"
    exit
fi
# Get encoding type
etype=$1

# Echo all commands
#set -x

# Create a temp file
tmpfile=$(mktemp foo.XXXXXX)
echo "This is the first line" > $tmpfile
echo "This is the second line" >> $tmpfile
echo "This is the third line" >> $tmpfile

# Test simple encoding and decoding
python hamming.py $etype enc $tmpfile ${tmpfile}.enc
python hamming.py $etype dec ${tmpfile}.enc ${tmpfile}.dec
diff ${tmpfile} ${tmpfile}.dec
res=$?
if [ $res -eq 0 ]; then
    echo "[PASS] simple encoding"
else
    echo "[FAIL] simple encoding"
fi

# Test error introduction 
python hamming.py $etype err 7 ${tmpfile}.enc ${tmpfile}.err1
python hamming.py $etype err 23 ${tmpfile}.err1 ${tmpfile}.err2

# Check to make sure errors were introduced
diff -a ${tmpfile}.enc ${tmpfile}.err2 &>/dev/null
res=$?
if [ $res -eq 1 ]; then
    echo "[PASS] error injection"
else
    echo "[FAIL] error injection"
    exit
fi

# Check error correction
python hamming.py $etype fix ${tmpfile}.err2 ${tmpfile}.fixed
python hamming.py $etype dec ${tmpfile}.fixed ${tmpfile}.dec2
diff ${tmpfile} ${tmpfile}.dec2
res=$?
if [ $res -eq 0 ]; then
    echo "[PASS] error correction"
else
    echo "[FAIL] error correction"
fi

# Removing generated files
rm ${tmpfile}*
