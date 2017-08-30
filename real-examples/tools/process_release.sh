mkdir -p tools/logs
logfile=`echo $1 | sed -e 's/\//_/g'`

cd tools

python convert_releases_to_bigquery_schema.py -f ../$1/all/releases/ | ts '[%Y-%m-%d %H:%M:%S]' | tee -a logs/$logfile.log

bq rm --project_id ocds-172716 new_releases.$2  | ts '[%Y-%m-%d %H:%M:%S]' | tee -a logs/$logfile.log
bq load --max_bad_records=100 --source_format=NEWLINE_DELIMITED_JSON --schema=release-schema-bq.json --project_id ocds-172716 new_releases.$2 staging/$1/all/releases/all.json | ts '[%Y-%m-%d %H:%M:%S]' | tee -a logs/$logfile.log
