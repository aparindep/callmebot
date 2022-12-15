from datetime import datetime
from functools import partial

from celery.schedules import crontab
import pytz
from pytz.tzinfo import DstTzInfo
from redbeat.decoder import RedBeatJSONDecoder, RedBeatJSONEncoder

# add nowfun support in redbeat entry

class CustomJSONDecoder(RedBeatJSONDecoder):
    def dict_to_object(self, d):
        if '__type__' not in d:
            return d
        
        objtype = d.pop('__type__')

        if objtype == 'crontab':
            if d.get('nowfun', {}).get('keywords', {}).get('zone'):
                d['nowfun'] = partial(datetime.now, tz = pytz.timezone(d.pop('nowfun')['keywords']['zone']))
            return crontab(**d)
        
        d['__type__'] = objtype

        return super().dict_to_object(d)

class CustomJSONEncoder(RedBeatJSONEncoder):
    def default(self, obj):
        if isinstance(obj, crontab):
            d = super().default(obj)
            if 'nowfun' not in d and isinstance(obj.nowfun, partial) and obj.nowfun.func == datetime.now:
                zone = None
                if obj.nowfun.args and isinstance(obj.nowfun.args[0], DstTzInfo):
                    zone = obj.nowfun.args[0].zone
                elif isinstance(obj.nowfun.keywords.get('tz'), DstTzInfo):
                    zone = obj.nowfun.keywords['tz'].zone
                if zone:
                    d['nowfun'] = {'keywords': {'zone': zone}}
            return d

        return super().default(obj)