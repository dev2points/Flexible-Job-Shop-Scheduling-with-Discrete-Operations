TO=3600
MO=14000

MDATA_DIR=Datasets/MPSFs
PDATA_DIR=Datasets/PSFs

MRESULT_DIR=Results/order_transitive+sb/MPSFs
PRESULT_DIR=Results/order_transitive+sb/PSFs

mkdir -p $MRESULT_DIR
mkdir -p $PRESULT_DIR
Datasets/PSFs/PSF06_15×7.txt


# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF01.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF01.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF02.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF02.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF03.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF03.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF04.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF04.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF05.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF05.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF06.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF06.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF07.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF07.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF08.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF08.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF09.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF09.log
# ./runlim -r $TO -s $MO  python3 -u main_ver2.py $MDATA_DIR/MPSF10.txt  --order_transitive --symmetry  2>&1  | tee $MRESULT_DIR/MPSF10.log

./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF01_10×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF01_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF02_10×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF02_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF03_10×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF03_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF04_10×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF04_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF05_10×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF05_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF06_15×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF06_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF07_15×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF07_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF08_15×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF08_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF09_15×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF09_15×7.log
./runlim -r $TO -s $MO  python3 -u main_ver2.py $PDATA_DIR/PSF10_15×7.txt  --order_transitive --symmetry  2>&1  | tee $PRESULT_DIR/PSF10_15×7.log



