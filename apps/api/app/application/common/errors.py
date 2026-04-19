class ApplicationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        detail: object | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail


class NotFoundError(ApplicationError):
    def __init__(self, message: str, *, detail: object | None = None) -> None:
        super().__init__(message, status_code=404, detail=detail)


class ConflictError(ApplicationError):
    def __init__(self, message: str, *, detail: object | None = None) -> None:
        super().__init__(message, status_code=409, detail=detail)
