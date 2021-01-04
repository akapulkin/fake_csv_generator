import lorem
import string
import csv
import os
import boto3
import tempfile

from django.conf import settings
from Fake_csv_generator.celery import app
from celery import shared_task
from random import randrange, randint, choice
from datetime import datetime

S3_BUCKET = os.environ.get('S3_BUCKET')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
S3_REGION = os.environ.get('S3_REGION')

@shared_task
def create_csv(dataset_data):
    file_path = settings.MEDIA_ROOT+'/temp.csv'
    file_path_bucket = str(dataset_data['dataset_id']) + '.csv'
    head_row = []
    col_types = []
    for key, val in dataset_data['columns'].items():
        head_row.append(key)
        col_types.append(val)
    row_data = data_generator(dataset_data['rows_quantity'], col_types)
    with open(file_path, mode='w') as csv_file:
        dataset_writer = csv.writer(csv_file, delimiter=dataset_data['delimiter'],
            quotechar=dataset_data['quotechar'],
            quoting=csv.QUOTE_MINIMAL)
        dataset_writer.writerow(head_row)
        for row in row_data:
            dataset_writer.writerow(row)
    s3 = boto3.client('s3', region_name=S3_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.upload_file(file_path, S3_BUCKET, file_path_bucket)
    return True


def data_generator(row_quant, col_types):
    results = []
    for a in col_types:
        if a['type'] == 'int':
            results.append(integer_generator(row_quant, a['from'], a['to']))
        elif a['type'] == 'email':
            results.append(email_generator(row_quant))
        elif a['type'] == 'phone_num':
            results.append(phone_generator(row_quant))
        elif a['type'] == 'text':
            results.append(text_generator(row_quant, a['from'], a['to']))
        elif a['type'] == 'date':
            results.append(date_generator(row_quant))
    return zip(*results)


def integer_generator(row_quant, renge_from, renge_to):
    i = 0
    int_list = []
    while i < row_quant:
        int_list.append(randrange(renge_from, renge_to))
        i += 1
    return int_list


def phone_generator(row_quant):
    i = 0
    phone_list = []
    while i < row_quant:
        foreign_code = str(randint(1, 99))
        local_code = str(randint(1, 9999)).zfill(4)
        p1 = (str(randint(1, 999)).zfill(3))
        p2 = (str(randint(1, 99)).zfill(2))
        p3 = (str(randint(1, 99)).zfill(2))
        phone_list.append(f'+{foreign_code}({local_code}){p1}-{p2}-{p3}')
        i += 1
    return phone_list


def date_generator(row_quant):
    i = 0
    date_list = []
    while i < row_quant:
        timestamp = randint(-1104537600, 1577836800)
        if timestamp == 0:
            timestamp += 1
        new_date = datetime.fromtimestamp(timestamp)
        date_list.append(new_date.strftime("%m/%d/%Y"))
        i += 1
    return date_list


def text_generator(row_quant, renge_from, renge_to):
    i = 0
    text_list = []
    while i < row_quant:
        text_list.append(lorem.get_sentence(count=randrange(renge_from, renge_to),
                                            word_range=(5, 9), sep=' '))
        i += 1
    return text_list


def email_generator(row_quant):
    domains = ['gmail.com', 'yahoo.com', 'mail.ru', 'ukr.net', 'list.ru', 'proton.mail',
               'outlook.com', 'bigmir.ua', 'rap.ru']
    i = 0
    email_list = []
    while i < row_quant:
        dom = domains[randint(0, len(domains) - 1)]
        account_len = randint(5, 12)
        account_name = ''.join(choice(string.ascii_lowercase +
                                      string.digits) for _ in range(account_len))
        new_email = account_name + "@" + dom
        email_list.append(new_email)
        i += 1
    return email_list

# TODO All Type data generator
