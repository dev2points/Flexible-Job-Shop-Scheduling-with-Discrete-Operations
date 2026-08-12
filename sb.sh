TO=3600
MO=14000

MDATA_DIR=Datasets/MPSFs

MRESULT_DIR=Results/sb/MPSFs

mkdir -p $MRESULT_DIR



# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF01.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF01.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF02.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF02.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF03.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF03.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF04.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF04.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF05.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF05.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF06.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF06.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF07.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF07.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF08.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF08.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF09.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF09.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF10.txt --symmetry 2>&1  | tee $MRESULT_DIR/MPSF10.log

