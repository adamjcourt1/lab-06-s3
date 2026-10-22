#!/bin/bash
set -euo pipefail

BOOK_URL=$1
SECRETBUCKET=$2
EXPIRE=$3
fname="${BOOK_URL##*/}"

# download into books/
curl -O --create-dirs --output-dir books "$BOOK_URL"

# create bucket if needed
if aws s3 ls "s3://$SECRETBUCKET" > /dev/null 2>&1; then
    echo 'Bucket already exists.'
else
    echo 'Creating bucket now.'
    aws s3 mb "s3://$SECRETBUCKET"
fi

aws s3 cp "books/$fname" "s3://$SECRETBUCKET/$fname" --content-type "text/plain; charset=utf-8"

aws s3 presign "s3://$SECRETBUCKET/$fname" --expires-in "$EXPIRE"