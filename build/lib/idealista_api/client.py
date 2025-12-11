import requests
from .utils import get_bearer_token
from .models import Response, Search
from .exceptions import APIException
from .consts import URL, ACCEPTED_COUNTRIES

time_format = "%Y-%m-%d %H:%M:%S"


class Idealista:
    """Idealista API client."""

    session: requests.Session

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        token: str | None = None,
    ):
        if token is not None:
            self.token = token
        elif api_key is not None and api_secret is not None:
            self.api_key = api_key
            self.api_secret = api_secret

            self.token = get_bearer_token(api_key=api_key, secret=api_secret)
        else:
            raise Exception(
                "No valid authentication method provided. Either a token or an API key and secret are required."
            )
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "idealista_api_python/1.0",
            }
        )

    def query(self, request: Search) -> Response:
        """
        Makes a query to Idealista's API.

        Args:
            request (Search): Request data, using parameters specified by the API documentation.

        Returns:
            list[Property]: List of properties returned by the API.
        """
        if request.country not in ACCEPTED_COUNTRIES:
            raise ValueError(f"Country '{request.country}' is not supported. Supported countries are: {', '.join(ACCEPTED_COUNTRIES)}")
        else:
            response = self.session.post(
                url=URL.format(country=request.country),
                data=request.to_json(),
            )
            
        response_dict = response.json()
        if response.status_code != 200:
            error_description = response_dict.get("error_description") or response_dict.get("message") or "No description available"
            raise APIException(
                f"Error querying API: {response_dict.get('error', 'Unknown error')} - {error_description}",
                response=response_dict
            )
        return Response(response_dict)
