from fastapi import HTTPException


def call_service(
    function,
    *args,
    error_status: int = 400,
    **kwargs
):

    try:

        return function(*args, **kwargs)

    except ValueError as error:

        raise HTTPException(
            status_code=error_status,
            detail=str(error)
        ) from error
