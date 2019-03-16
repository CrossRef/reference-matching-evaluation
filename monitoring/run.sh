#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
NAME=$1

DATE=$(date +"%Y-%m-%d %H:%M:%S")
OUT=$(mktemp)
LOG=$(mktemp)

touch $DIR/plugins/$NAME/results.csv
cp $DIR/plugins/$NAME/results.csv $LOG
$DIR/plugins/$NAME/run $DIR/plugins/$NAME/ > $OUT 2>> $DIR/plugins/$NAME/log

if [ -s $OUT ]
then
	RESULT="$DATE,$(cat $OUT)"
	echo $RESULT >> $LOG
	mv $LOG $DIR/plugins/$NAME/results.csv
	/usr/local/bin/jupyter nbconvert --log-level WARN --execute $DIR/monitoring.ipynb
else
        echo "Error running $NAME"
fi

rm $OUT
