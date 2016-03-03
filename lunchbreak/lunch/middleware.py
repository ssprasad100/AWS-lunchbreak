from __future__ import print_function

import traceback


class PrintExceptionMiddleware(object):

    def process_exception(self, request, exception):
        traceback.print_exc()
