from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        details = response.data
        response.data.update(
            {
                "status_code": response.status_code,
            }
        )
        # for detail in details.get("detail"):
        #     err = detail.split(":")
        #     response.data.updated({f"{err[0]}":f"{err[1]}"})

    return response
