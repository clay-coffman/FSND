import os
from flask import jsonify, abort, make_response, request
from app import db
from app.models import Movie, Actor
from functools import wraps
from jose import jwt

from app.main import bp

# TODO move to config
AUTH0_DOMAIN = "domain"
API_AUDIENCE = "coffee-shop-endpoint"
ALGORITHMS = ["RS256"]


# TODO routes
# GET/ Actors and movies
# DELETE/ Actors and movies
# POST/ Actors and movies
# PATCH/ Actors and movies

# TODO roles
# Casting Assistant - can view actors and movies
# Casting Director - full crud for actors, update only for movies
# Executive Producer - full crud for actors and movies


@bp.route("/", methods=["GET"])
def get_greeting():
    return "greetings"


@bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify(users=[u.format for u in users])


@bp.route("/users", methods=["POST"])
def create_user():
    if requires_scope("create:user"):

        body = request.get_json()

        if body is None:
            raise GenericError(
                {
                    "code": "Invalid Request",
                    "description": "The request is invalid, see documentation",
                },
                422,
            )

        username = body.get("username")
        first_name = body.get("first_name")
        last_name = body.get("last_name")
        email = body.get("email")

        if not all([username, first_name, last_name, email]):
            raise GenericError(
                {
                    "code": "Invalid Request",
                    "description": "The request is invalid, see documentation",
                },
                422,
            )

        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        new_user.insert()

        res = make_response(jsonify(new_user.format()), 201)

        return res
    raise AuthError(
        {
            "code": "Unauthorized",
            "description": "You don't have the necessary privileges to perform this action",
        },
        403,
    )


# Format error response and append status code


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError(
            {
                "code": "authorization_header_missing",
                "description": "Authorization header is expected",
            },
            401,
        )

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must start with" " Bearer",
            },
            401,
        )
    elif len(parts) == 1:
        raise AuthError(
            {"code": "invalid_header", "description": "Token not found"}, 401
        )
    elif len(parts) > 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must be" " Bearer token",
            },
            401,
        )

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
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
            except jwt.ExpiredSignatureError:
                raise AuthError(
                    {
                        "code": "token_expired",
                        "description": "token is expired",
                    },
                    401,
                )
            except jwt.JWTClaimsError:
                raise AuthError(
                    {
                        "code": "invalid_claims",
                        "description": "incorrect claims,"
                        "please check the audience and issuer",
                    },
                    401,
                )
            except Exception:
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Unable to parse authentication"
                        " token.",
                    },
                    401,
                )

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Unable to find appropriate key",
            },
            401,
        )

    return decorated


def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False


# TODO: add error handlers
# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class GenericError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(GenericError)
def handle_generic_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
