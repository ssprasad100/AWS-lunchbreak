from rest_framework.response import Response
from Lunchbreak.exceptions import lunchbreakExceptionHandler


class LunchbreakResponse(Response):

    def __init__(self, detail=None, status_code=None, exception=None, template_name=None, headers=None, content_type=None):
        if exception is None:
            status_code = self.status_code if status_code is None else status_code
            data = {
                'error': {
                    'code': self.code,
                    'information': self.information
                }
            }

            if detail is not None:
                data['error']['detail'] = detail
        else:
            response = lunchbreakExceptionHandler(exception)
            data = response.data

        super(LunchbreakResponse, self).__init__(data, status_code, template_name, headers, content_type)
