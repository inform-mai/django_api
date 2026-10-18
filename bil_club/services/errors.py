class ServiceError(Exception):
    code = 400

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(ServiceError):
    code = 404


class ValidationError(ServiceError):
    code = 422


class ForbiddenError(ServiceError):
    code = 403


class NotImplementedError(ServiceError):
    code = 501
