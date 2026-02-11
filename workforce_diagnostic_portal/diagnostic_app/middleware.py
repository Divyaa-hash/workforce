class RoleMiddleware:
    """Middleware to add role information to request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data') and request.user.is_authenticated:
            if response.context_data is None:
                response.context_data = {}
            response.context_data['user_role'] = request.user.role
            response.context_data['user_level'] = request.user.get_level()
        return response