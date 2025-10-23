from enum import Enum

class AuthType(Enum):
    PASSWORD = "password"
    JWT = "jwt"
    OAUTH = "oauth"