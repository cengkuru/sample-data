mkdir -p tools/logs
logfile=`echo $1 | sed -e 's/\//_/g'`

python update_to_v1_1.py -f $1/all/releases | ts '[%Y-%m-%d %H:%M:%S]' | tee -a tools/logs/$logfile.log
python validate.py -f $1/all/releases | ts '[%Y-%m-%d %H:%M:%S]' | tee -a tools/logs/$logfile.log
