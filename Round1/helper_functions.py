import os, re, datetime, json, uuid
from Round1.settings import BASE_DIR, DEBUG


def convert_date_to_epoch(date):
    return int(date.strftime('%s'))*1000 if date else None

def convert_epoch_to_date(epoch):
    return datetime.datetime.fromtimestamp(int(epoch)/1000.0) if epoch else None

def convert_time_to_epoch(time):
    return int(datetime.datetime.now().replace(hour=time.hour, minute=time.minute, second=0, microsecond=0).strftime('%s'))*1000 if time else None

def convert_epoch_to_time(epoch):
    return datetime.datetime.fromtimestamp(int(epoch)/1000.0).time() if epoch else None

def get_params(request):
    try:
        return json.loads(str(request.body, 'utf-8'))
    except Exception as e:
        print('Error in get_params, request.body not found: ', e)
        return {}

