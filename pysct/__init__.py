#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
 
__version__ = '0.0.3'
__author__ = 'SAS'
__credits__ = ['Eduardo Hellas']
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright © 2020, SAS Institute Inc., ' \
                'Cary, NC, USA.  All Rights Reserved.'

import logging
import sys

if sys.version_info < (3, ):
    from warnings import warn
    warn('You are using Python %d.%d which was officially sunset on January 1st, 2020.  '
         'This package only supports python 3.6 or higher.' % (sys.version_info.major, sys.version_info.minor),
         UserWarning, 2)

from .datastep_translators import *
from .nlp_translator import *

# Prevent package from emitting log records unless consuming
# application configures logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())