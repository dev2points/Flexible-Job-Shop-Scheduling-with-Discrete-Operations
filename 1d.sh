TO=3600
MO=14000

MDATA_DIR=Datasets/MPSFs

MRESULT_DIR=Results/1d/MPSFs

mkdir -p $MRESULT_DIR



# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF01.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF01.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF02.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF02.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF03.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF03.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF04.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF04.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF05.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF05.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF06.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF06.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF07.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF07.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF08.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF08.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF09.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF09.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF10.txt --sm_mode 1d 2>&1  | tee $MRESULT_DIR/MPSF10.log

