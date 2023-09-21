import os

from dotenv import load_dotenv
from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2
# from social_core.backends.elixir import ElixirOpenIdConnect
from social_core.backends.open_id_connect import OpenIdConnectAuth

from fastapi_oauth2.claims import Claims
from fastapi_oauth2.client import OAuth2Client
from fastapi_oauth2.config import OAuth2Config

load_dotenv()

class HelmholtzOpenIdConnect(OpenIdConnectAuth):
    name = "helmholtz"
    OIDC_ENDPOINT = "https://login.helmholtz.de/oauth2"
    EXTRA_DATA = [
        ("expires_in", "expires_in", True),
        ("refresh_token", "refresh_token", True),
        ("id_token", "id_token", True),
        ("other_tokens", "other_tokens", True),
    ]
    # In order to get any scopes, you have to register your service with
    # ELIXIR, see documentation at
    # https://www.elixir-europe.org/services/compute/aai
    DEFAULT_SCOPE = ["openid", "email"]
    JWT_DECODE_OPTIONS = {"verify_at_hash": False}

    ID_TOKEN_ISSUER = "https://login.helmholtz.de/oauth2"
    ACCESS_TOKEN_URL = "https://login.helmholtz.de/oauth2/token"
    AUTHORIZATION_URL = "https://login.helmholtz.de/oauth2-as/oauth2-authz"
    REVOKE_TOKEN_URL = "https://login.helmholtz.de/oauth2/revoke"
    USERINFO_URL = "https://login.helmholtz.de/oauth2/userinfo"
    JWKS_URI = "https://login.helmholtz.de/oauth2/jwk"
    TOKEN_ENDPOINT_AUTH_METHOD = "https://login.helmholtz.de/oauth2/token"


    def get_user_details(self, response):
        logger.debug(F"get_user_details")
        username_key = self.setting("USERNAME_KEY", default=self.USERNAME_KEY)
        name = response.get("name") or ""
        fullname, first_name, last_name = self.get_user_names(name)
        return {
            "username": response.get(username_key),
            "email": response.get("email"),
            "fullname": fullname,
            "first_name": first_name,
            "last_name": last_name,
        }

oauth2_config = OAuth2Config(
    allow_http=True,
    jwt_secret=os.getenv("JWT_SECRET"),
    jwt_expires=os.getenv("JWT_EXPIRES"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM"),
    clients=[
        OAuth2Client(
            backend=GithubOAuth2,
            client_id=os.getenv("OAUTH2_GITHUB_CLIENT_ID"),
            client_secret=os.getenv("OAUTH2_GITHUB_CLIENT_SECRET"),
            scope=["user:email"],
            claims=Claims(
                picture="avatar_url",
                identity=lambda user: f"{user.provider}:{user.id}",
            ),
        ),
        OAuth2Client(
            backend=GoogleOAuth2,
            client_id=os.getenv("OAUTH2_GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("OAUTH2_GOOGLE_CLIENT_SECRET"),
            scope=["openid", "profile", "email"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
            ),
        ),
        OAuth2Client(
            backend=HelmholtzOpenIdConnect,
            client_id="alise",
            client_secret="---",
            redirect_uri="http://127.99.0.1:8000/marcus",
            scope=["openid", "profile", "email"],
            claims=Claims(
                identity=lambda user: f"{user.provider}:{user.sub}",
            ),
        ),
    ]
)
