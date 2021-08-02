import os
import json
from typing import Tuple, Union
from urllib.request import urlopen
from jose import jwt

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("API_AUDIENCE")
ALGORITHMS = ["RS256"]
PERMISSION = os.getenv("PERMISSION")


class AuthError:
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


def get_token_from_auth_header(req) -> Tuple[str, Union[AuthError, None]]:
    auth_header = req.headers.__http_headers__.get("authorization", "")
    if not auth_header:
        return ("", AuthError("Authorization header is missing", 401))
    header_parts = auth_header.split()
    if header_parts[0].lower() != "bearer":
        return ("", AuthError("Invalid Header: must start with Bearer.", 401))
    if len(header_parts) == 1:
        return ("", AuthError("Invalid Header: Missing token", 401))
    if len(header_parts) > 2:
        return ("", AuthError("Invalid Header: Must be bearer token", 401))
    return (header_parts[1], None)


def check_permissions(permission, payload) -> Union[AuthError, None]:
    permissions = payload.get("permissions", None)
    if permissions is None:
        return AuthError("Bad request: No permissions exist", 400)
    if permission not in permissions:
        return AuthError("Unauthorized request", 403)


def verify_decode_jwt(token) -> Tuple[dict, Union[AuthError, None]]:
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        return (
            {},
            AuthError("Invalid Header: Unable to parse authentication token", 400),
        )
    rsa_key = {}
    if "kid" not in unverified_header:
        return ({}, AuthError("Invalid Header: Authorization malformed.", 401))

    # Checks if the JWT token is a valid token signed by Auth0 serivce.
    # Those key properties are used to verify the JWT signature.
    # For extra info refer to: https://auth0.com/docs/tokens/json-web-tokens/json-web-key-set-properties
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/",
            )

            return (payload, None)

        except jwt.ExpiredSignatureError:
            return ({}, AuthError("Error: Token Expired", 401))

        except jwt.JWTClaimsError:
            return (
                {},
                AuthError(
                    "Invalid claims:Please check the audience and the issuer", 401
                ),
            )
        except Exception:
            return (
                {},
                AuthError("Invalid Header: Unable to parse authentication token", 400),
            )
    return ({}, AuthError("Invalid Header: Unable to find the appropriate key.", 400))
