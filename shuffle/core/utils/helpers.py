import json
import datetime
import logging
import urllib
import os
import re

from django.conf import settings
from django.utils import timezone

from oauth2_provider.generators import generate_client_secret as generate_random_alphanumeric

logger = logging.getLogger(__name__)

def generate_activation_code(limit=None):
    return generate_random_alphanumeric()[:(limit or settings.USER_ACTIVATION_CODE_LENGTH)]

def get_time(days=5):
    return (timezone.now() + datetime.timedelta(days=days))

def access_code_expires_on(days=30):
    return get_time(days=days)

def password_reset_expires_on(days=3):
    return get_time(days=days)

def activation_code_expires_on(days=3):
    return get_time(days=days)

def extract_body(request, *args, **kwargs):

    try:
        data = json.loads(request.body)
    except Exception:
        data = {}
        logger.error(
            json.dumps(dict(message="Error decoding data submitted.", args=args, kwargs=kwargs)), exc_info=True)
        
    return data

def create_database_url(database_dict, base_dir=None):
    if database_dict:
        database_dict = database_dict.copy()

        if 'sqlite' in (database_dict.get('ENGINE') or ''):
            if base_dir is None:
                return

            return "sqlite:///%s" % (base_dir.child(database_dict.get('NAME')) or '')
        else:
            if 'PASSWORD' in database_dict:
                database_dict['PASSWORD'] = urllib.quote_plus(database_dict['PASSWORD'])
            
            if 'post' in (database_dict.get('ENGINE') or ''):
                database_dict['PORT'] = 5432
                return "postgres://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s" % database_dict
            elif 'mysql' in (database_dict.get('ENGINE') or ''):
                database_dict['PORT'] = 3306
                return "mysql://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s" % database_dict

def get_file_location(instance, filename, prepend=None, specific_folder=None, by_date=False, getter=None, prepare=False):
    args = tuple()

    if getter is None:
        def _getter(instance):
            return str(instance) 
        getter = _getter

    if prepend is not None:
        args += (prepend,)

    args += (getter(instance),)

    if specific_folder is not None:
        args += (specific_folder,)

    if by_date:
        args += (timezone.now().strftime("%Y/%m/%d"),)

    args += (filename,)

    file_location = os.path.join(*args)

    if prepare:
        from django.core.files.storage import default_storage
        default_storage.generate_filename(file_location)

    return file_location

def is_valid_phone_number(phone_number):
    if re.match(r"^(\+?254|0)(70|71|72|79|74[0-6]|748|757|759|76[89]|11[012345])[\d]{6,7}$", phone_number):
        return True
    return False

def parse_date(date, format="%d-%b-%y", formats=None, to_date=True):
    if formats is None:
        formats = settings.DEFAULT_DATETIME_INPUT_FORMATS

    for _format in formats:
        if date:
            try:
                parsed_date = datetime.datetime.strptime(date, _format)
                return parsed_date.date() if to_date else parse_date
            except (ValueError, TypeError):
                pass

    if format:
        parsed_date = datetime.datetime.strptime(date, format)
        return parsed_date.date() if to_date else parse_date

def format_date(date, format="%d-%m-%Y"):
    return datetime.datetime.strftime(date, format)

def exception_to_json(exception):
    if settings.DEBUG:
        import traceback

        exception_data = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'stack_trace': traceback.format_exception(
                type(exception), 
                exception, 
                exception.__traceback__
            )
        }
        
        return json.dumps(exception_data)