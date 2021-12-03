from dataclasses import asdict, dataclass
from typing import List

import requests
from requests.auth import AuthBase

from argo_workflow_tools.argo_options import ArgoOptions


class ArgoApiException(Exception):
    def __init__(self, status=None, reason=None, http_resp=None):
        if http_resp:
            self.status = http_resp.status
            self.reason = http_resp.reason
            self.body = http_resp.data
            self.headers = http_resp.getheaders()
        else:
            self.status = status
            self.reason = reason
            self.body = None
            self.headers = None

    def __str__(self):
        """Custom error messages for exception"""
        error_message = "({0})\n" "Reason: {1}\n".format(self.status, self.reason)
        if self.headers:
            error_message += "HTTP response headers: {0}\n".format(self.headers)

        if self.body:
            error_message += "HTTP response body: {0}\n".format(self.body)

        return error_message


@dataclass
class SubmitOptions:
    parameters: List[str]
    labels: str


@dataclass
class ArgoSubmitRequestBody:
    namespace: str
    resourceKind: str = "WorkflowTemplate"
    resourceName: str = None
    submitOptions: SubmitOptions = None


class HTTPArgoAuth(AuthBase):
    """Attaches HTTP Basic Authentication to the given Request object."""

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return all(
            [
                self.token == getattr(other, "token", None),
            ]
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers["Authorization"] = self.token
        return r


class ArgoHttpClient:
    def __init__(self, url, argo_options: ArgoOptions):
        self._argo_options = argo_options
        self._url = url

    def _get_authorization(self):
        if self._argo_options.authorization_token:
            return HTTPArgoAuth(self._argo_options.authorization_token)
        return None

    def submit_workflow(self, namespace, body: ArgoSubmitRequestBody):
        response = requests.post(
            f"{self._url}/api/v1/workflows/{namespace}/submit",
            json=asdict(body),
            auth=self._get_authorization(),
        )
        if response.status_code != 200:
            raise ArgoApiException(
                status=response.status_code, reason=response.reason, http_resp=response
            )
        return response.json()

    def create_workflow(self, namespace, body: dict):
        response = requests.post(
            f"{self._url}/api/v1/workflows/{namespace}",
            json={"workflow": body},
            auth=self._get_authorization(),
        )
        if response.status_code != 200:
            raise ArgoApiException(
                status=response.status_code, reason=response.text, http_resp=response
            )
        return response.json()

    def get_workflow(self, namespace, name):
        response = requests.get(
            f"{self._url}/api/v1/workflows/{namespace}/{name}",
            auth=self._get_authorization(),
        )
        if response.status_code != 200:
            raise ArgoApiException(
                status=response.status_code, reason=response.reason, http_resp=response
            )
        return response.json()

    def workflow_resume(self, namespace, name):
        response = requests.put(
            f"{self._url}/api/v1/workflows/{namespace}/{name}/resume",
            auth=self._get_authorization(),
        )
        if response.status_code != 200:
            raise ArgoApiException(
                status=response.status_code, reason=response.reason, http_resp=response
            )
        return response.json()

    def workflow_retry(self, namespace, name):
        response = requests.put(
            f"{self._url}/api/v1/workflows/{namespace}/{name}/retry",
            auth=self._get_authorization(),
        )
        if response.status_code != 200:
            raise ArgoApiException(
                status=response.status_code, reason=response.reason, http_resp=response
            )
        return response.json()

    def workflow_stop(self, namespace, name):
        response = requests.put(
            f"{self._url}/api/v1/workflows/{namespace}/{name}/stop",
            auth=self._get_authorization(),
        )
        if response.status_code != 200:
            raise ArgoApiException(
                status=response.status_code, reason=response.reason, http_resp=response
            )
        return response.json()

    def workflow_suspend(self, namespace, name):
        response = requests.put(
            f"{self._url}/api/v1/workflows/{namespace}/{name}/suspend",
            auth=self._get_authorization(),
        )
        if response.status_code != 200:
            raise ArgoApiException(
                status=response.status_code, reason=response.reason, http_resp=response
            )
        return response.json()
