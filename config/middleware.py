# config/middleware.py

class HTMXMiddleware:
    """
    Middleware pour ajouter le support HTMX aux requêtes Django
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ajouter l'attribut htmx à la requête
        request.htmx = self.is_htmx(request)

        response = self.get_response(request)
        return response

    def is_htmx(self, request):
        """
        Vérifie si la requête provient de HTMX
        """
        return request.headers.get('HX-Request') == 'true'