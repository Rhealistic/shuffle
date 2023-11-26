from __future__ import absolute_import, unicode_literals

import datetime
import decimal
import uuid

from django.utils.duration import duration_iso_string
from django.utils.timezone import is_aware

try:
    from simplejson import *

    class _JSONEncoder(JSONEncoder):
        def default(self, o):
            # See "Date Time String Format" in the ECMA-262 specification.
            if isinstance(o, datetime.datetime):
                r = o.isoformat()
                if o.microsecond:
                    r = r[:23] + r[26:]
                if r.endswith('+00:00'):
                    r = r[:-6] + 'Z'
                return r
            elif isinstance(o, datetime.date):
                return o.isoformat()
            elif isinstance(o, datetime.time):
                if is_aware(o):
                    raise ValueError("JSON can't represent timezone-aware times.")
                r = o.isoformat()
                if o.microsecond:
                    r = r[:12]
                return r
            elif isinstance(o, datetime.timedelta):
                return duration_iso_string(o)
            elif isinstance(o, decimal.Decimal):
                return str(o)
            elif isinstance(o, uuid.UUID):
                return str(o)
            else:
                return super(_JSONEncoder, self).default(o)

except ImportError:
    from json import *

    class _JSONEncoder(JSONEncoder):
        def default(self, o):
            # See "Date Time String Format" in the ECMA-262 specification.
            if isinstance(o, datetime.datetime):
                r = o.isoformat()
                if o.microsecond:
                    r = r[:23] + r[26:]
                if r.endswith('+00:00'):
                    r = r[:-6] + 'Z'
                return r
            elif isinstance(o, datetime.date):
                return o.isoformat()
            elif isinstance(o, datetime.time):
                if is_aware(o):
                    raise ValueError("JSON can't represent timezone-aware times.")
                r = o.isoformat()
                if o.microsecond:
                    r = r[:12]
                return r
            elif isinstance(o, datetime.timedelta):
                return duration_iso_string(o)
            elif isinstance(o, decimal.Decimal):
                return str(o)
            elif isinstance(o, uuid.UUID):
                return str(o)
            elif isinstance(o, CallableBool):
                return bool(o)
            else:
                return super(_JSONEncoder, self).default(o)

old_dumps = dumps
def __dumps(*args, **kwargs):
    return old_dumps(cls=_JSONEncoder, *args, **kwargs)
dumps = __dumps