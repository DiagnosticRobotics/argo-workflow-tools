class ArgoOptions:
    def __init__(
        self,
        logger: callable = print,
        client_side_validation: bool = True,
        namespace="argo",
        polling_interval: float = 1.0,
        authorization_token: str = None,
    ):
        self.client_side_validation = client_side_validation
        self.namespace = namespace
        self.logger = logger
        self.polling_interval = polling_interval
        self.authorization_token = authorization_token
