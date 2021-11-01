class ArgoOptions:
    def __init__(
        self,
        logger: callable = print,
        client_side_validation: bool = True,
        namespace="argo",
        polling_interval: float = 1.0,
        authorization_token: str = None,
    ):
        """[summary]

        Args:
            logger (callable, optional): logger function. Defaults to print.
            client_side_validation (bool, optional): enable client side SSL validation. Defaults to True.
            namespace (str, optional): default namespace. Defaults to "argo".
            polling_interval (float, optional): workflows status polling interval when waiting for workflow to completes. Defaults to 1 second.
            authorization_token (str, optional): authorization token. Defaults to None.
        """
        self.client_side_validation = client_side_validation
        self.namespace = namespace
        self.logger = logger
        self.polling_interval = polling_interval
        self.authorization_token = authorization_token
