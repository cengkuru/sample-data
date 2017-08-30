mkdir -p tools/logs
logfile=`echo $1 | sed -e 's/\//_/g'`

python merge_releases.py --filepath $1/all/releases  --outfilepath $1/all/records | ts '[%Y-%m-%d %H:%M:%S]' | tee -a tools/logs/$logfile.log

cd tools 

python convert_releases_to_bigquery_schema.py -f ../$1/all/records/ | ts '[%Y-%m-%d %H:%M:%S]' | tee -a logs/$logfile.log

bq rm --project_id ocds-172716 new_records.$2  | ts '[%Y-%m-%d %H:%M:%S]' | tee -a logs/$logfile.log
bq load --max_bad_records=100 --source_format=NEWLINE_DELIMITED_JSON --schema=release-schema-bq.json --project_id ocds-172716 new_records.$2 staging/$1/all/records/all.json | ts '[%Y-%m-%d %H:%M:%S]' | tee -a logs/$logfile.log

cd ../