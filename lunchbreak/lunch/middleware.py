import traceback


class PrintExceptionMiddleware(object):

    def process_exception(self, request, exception):
        traceback.print_exc()
