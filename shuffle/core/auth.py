from rest_framework.authentication import SessionAuthentication as DRFSessionAuthentication

class SessionAuthentication(DRFSessionAuthentication):
    def enforce_csrf(self, _):
        return