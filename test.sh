TO=3600
MO=14000

MDATA_DIR=Datasets/MPSFs

MRESULT_DIR=Results/test/order_transitive+sb

mkdir -p $MRESULT_DIR




# ./runlim -r $TO -s $MO  python3 -u main_ver3.py $MDATA_DIR/MPSF09.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF09_ver3.log
# ./runlim -r $TO -s $MO  python3 -u main_ver4.py $MDATA_DIR/MPSF09.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF09_ver4.log
# ./runlim -r $TO -s $MO  python3 -u main_ver3.py $MDATA_DIR/MPSF09.txt  --order_transitive --symmetry --full_transitive 2>&1  | tee $MRESULT_DIR/MPSF09_ver3_full.log
# ./runlim -r $TO -s $MO  python3 -u main_ver4.py $MDATA_DIR/MPSF09.txt  --order_transitive --symmetry --full_transitive 2>&1  | tee $MRESULT_DIR/MPSF09_ver4_full.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF09.txt  --order_transitive --symmetry --full_transitive 2>&1  | tee $MRESULT_DIR/MPSF09_ver2_full.log
    


