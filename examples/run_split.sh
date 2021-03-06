WORKING_DIR=$(mktemp -d)

python3 dataset/draw_sample.py -s 10 -o $WORKING_DIR/sample.json
python3 dataset/generate_dataset.py -l ieee,apa -a "publisher,type"  -s $WORKING_DIR/sample.json -o $WORKING_DIR/dataset.json
python3 matching/match_references.py -d $WORKING_DIR/dataset.json -o $WORKING_DIR/matched.json
python3 evaluation/evaluate.py -d $WORKING_DIR/matched.json -s type -o $WORKING_DIR/outputdoc.csv -p $WORKING_DIR/outputsplit.csv
