import requests
import logging

from functools import cache


log = logging.getLogger(__name__)


def build_messages(role: str, *messages: str) -> list[dict]:
    return [{"role": role, "content": x} for x in messages]


class GPTAPIError(Exception):

    def __init__(self, response: requests.Response):
        super().__init__()
        self.status_code = response.status_code
        self.response = response



class GPTMisbehaveError(Exception):
    """ thrown when the AI did not generate what it was supposed to generate. """
    pass


class ChatGPTAPI:
    """ Wrapper around the ChatGpt API, used by the generator """

    BASE_URL = 'https://api.openai.com'

    def __init__(
            self,
            token: str,
            model: str,
            api_version: int = 1,
            project: str | None = None,
            organization: str | None = None
    ):
        self.token = token
        self.model = model
        self.api_version = api_version
        self.project = project or "default project"
        self.organization = organization
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if organization:
            self.headers["organization"] = organization
        if project:
            self.headers["project"] = project
        self.last_batch: str = ""

    @cache
    def _build_request_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}/v{self.api_version}/{endpoint}"

    def create_completion(self, messages: list[dict], temperature: int = 1, response_format: dict | None = None) -> str:
        response = requests.post(
            self._build_request_url("chat/completions"),
            None,
            {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "response_format": response_format
            },
            headers=self.headers
        )
        if response.ok:
            json_response = response.json()
            log.info(json_response)
            content = json_response["choices"][0]["message"]["content"]
            log.debug(f"AI input:\n\n{messages}\n\nAI output:\n\n{content}")
            return content
        log.error(f"could not create completion, response: {response.text}")
        raise GPTAPIError(response)

    def create_batch_line(self, messages: list[dict]) -> str:
        # TODO (?) adding batches would half the cost of API calls
        pass
