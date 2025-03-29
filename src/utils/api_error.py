class ApiError(Exception):
    """Class đại diện cho lỗi API custom"""

    def __init__(self, status_code, message):
        """
        Khởi tạo ApiError
        :param status_code: HTTP status code (int)
        :param message: Thông báo lỗi (str)
        """
        super().__init__(message) 
        self.status_code = status_code
        self.message = message

    def to_dict(self):
        """Chuyển error thành dict JSON"""
        return {"error": {"status_code": self.status_code, "message": self.message}}
