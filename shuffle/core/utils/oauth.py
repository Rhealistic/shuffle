from oauth2_provider.oauth2_validators import OAuth2Validator as BaseOAuth2Validator

class OAuth2Validator(BaseOAuth2Validator):
    def validate_user(self, *args, **kwargs):
        """
        Check username and password correspond to a valid and active User
        """
        return super(OAuth2Validator, self).validate_user(*args, **kwargs)