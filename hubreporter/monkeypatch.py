from __future__ import with_statement
from urllib2 import BaseHandler, parse_keqv_list, parse_http_list
import time, os, sys, threading
from contextlib import contextmanager

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#missing_syms = dict(BaseHandler = BaseHandler,
#                    parse_http_list = parse_http_list,
#                    parse_keqv_list = parse_keqv_list,
#                    time = time,
#                    os = os)
#
#def fixtwill():
#    for (k, v) in missing_syms.items():
#        __builtins__[k] = v
#    import twill.other_packages._mechanize_dist._auth
#
#def unfixtwill():
#    for k in missing_syms:
#        del __builtins__[k]
#
#@contextmanager
#def twillpatch():
#    fixtwill()
#    yield
#    unfixtwill()
#
#import twill.commands
#
#_go = twill.commands.go
#
#def go(*args, **kw):
#    with threading.Lock():
#        with twillpatch():
#            return _go(*args, **kw)
#
#twill.commands.go = go
