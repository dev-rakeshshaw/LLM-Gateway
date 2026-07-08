class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"{request.method} {request.path}")

        response = self.get_response(request)

        print("Status:", response.status_code)
        return response