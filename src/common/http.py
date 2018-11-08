from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class SuccessResponse(Response):
    def __init__(self, data=None, code=None, message=None, default_status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        selected_status = default_status if default_status else status.HTTP_200_OK
        wrapped_data = {
            'code': code if code else 1,
            'message': message if message else "OK",
            'status': selected_status,
            "data": data,
        }
        super(SuccessResponse, self).__init__(wrapped_data, selected_status, template_name, headers, exception,
                                              content_type)


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status'] = response.status_code
        response.data['message'] = response.data['detail']
        response.data['code'] = exc.get_codes()
        del response.data['detail']

    return response