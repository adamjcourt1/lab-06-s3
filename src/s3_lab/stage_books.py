#! /usr/bin/env python3

import logging
import os
import boto3
import sys
import requests
import time
import json

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

s3 = boto3.client("s3", region_name="us-east-1")

def parse_args():
    try:
        booklist = sys.argv[1]
        log.info(f"Book list file received.")
        indexpage = sys.argv[2]
        log.info(f"Index path received.")
        bucketname = sys.argv[3]
        log.info(f"Destination bucket path received.")
    except IndexError as e:
        log.info(f"File parsing failed: Fewer than 3 arguments given. {e}")
        sys.exit(1)
    return (booklist, indexpage, bucketname)

def download_books(list_file, dest_dir):
    path_list = []
    os.makedirs(dest_dir, exist_ok=True)
    with open(list_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    for line in lines:
        fname = line.strip().split('/')[-1]
        path = os.path.join(dest_dir, fname)
        if not os.path.exists(path):
            try:
                response = requests.get(line.strip(), timeout=30)
                time.sleep(1)
                with open(path, 'w') as f:
                    f.write(response.text)
                    log.info(f'Written file {fname}.')
            except requests.RequestException as e:
                log.info(f'Retrieval from url {line.strip()} failed. {e}')
        else:
            log.info(f'File {fname} already present in {dest_dir}. Skipping...')
        path_list.append(fname)
    return path_list

def create_bucket(bucket):
    try:
        s3.head_bucket(Bucket=bucket)
        log.info(f"Bucket {bucket} exists.")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            s3.create_bucket(Bucket=bucket)
            log.info(f"Created bucket: {bucket}")
            return True
        else:
            log.info(f"Bucket creation/verification failed.")
            return False

def make_public(bucket):
    s3.put_public_access_block(
    Bucket=bucket,
    PublicAccessBlockConfiguration={
        "BlockPublicAcls": False,
        "IgnorePublicAcls": False,
        "BlockPublicPolicy": False,
        "RestrictPublicBuckets": False,
    },
    )
    time.sleep(3)
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket}/*"
            }
        ]
    }

    s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))

def upload_files(bucket, file_paths):
    for item in file_paths:
        try:
            with open(f'books/{item}', "rb") as f:
                s3.put_object(
                    Bucket=bucket,
                    Key=item,
                    Body=f,
                    ContentType="text/plain",  # so browsers can display, not download
                )
            log.info(f"Uploaded {item} to s3://{bucket}/{item}")
        except FileNotFoundError:
            log.error(f"Local file not found: {item}")
        except ClientError as e:
            log.error(f"Error uploading object: {e}")

def upload_index(bucket, index_path):
    try:
        with open(index_path, "rb") as f:
            s3.put_object(
                Bucket=bucket,
                Key=index_path,
                Body=f,
                ContentType="text/html",  # so browsers can display, not download
            )
        log.info(f"Uploaded {index_path} to s3://{bucket}/{index_path}")
    except FileNotFoundError:
        log.error(f"Local file not found: {index_path}")
    except ClientError as e:
        log.error(f"Error uploading object: {e}")

def main():
    cl_args = parse_args()
    book_list = download_books(cl_args[0], 'books')
    create_bucket(cl_args[2])
    make_public(cl_args[2])
    upload_files(cl_args[2], book_list)
    upload_index(cl_args[2], cl_args[1])

if __name__ == "__main__":
    main()