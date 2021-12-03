from typing import Union

import shortuuid
from argo_workflow_tools.models.io.argoproj.workflow import v1alpha1 as argo

shortuuid = shortuuid.ShortUUID(alphabet="abcdefghijklmnopqrstuvwxyz1234567890")


def delete_none(_dict: dict) -> dict:
    if isinstance(_dict, list):
        for item in _dict:
            delete_none(item)
        return _dict
    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, dict):
                delete_none(value)
            if isinstance(value, list):
                delete_none(value)
            elif value is None:
                _dict.pop(key)
        return _dict
    return _dict


def _convert_params(
    args: Union[dict[str, str], list[Union[argo.Arguments, argo.Parameter]]]
) -> tuple[list[argo.Artifact], list[argo.Parameter]]:
    if isinstance(args, dict):
        parameters = [
            argo.Parameter(name=sanitize_name(key), value=value)
            for key, value in args.items()
        ]
        artifacts = []
        return parameters, artifacts

    if isinstance(args, list):
        parameters = list(filter(lambda arg: isinstance(arg, argo.Parameter), args))
        artifacts = list(filter(lambda arg: isinstance(arg, argo.Artifact), args))
        return parameters, artifacts

    raise ValueError(
        "args can be a list or Artifact and Parameters "
        "or a key-value dictionary representing key-value parameters"
    )


def get_arguments(
    args: Union[dict[str, str], list[Union[argo.Arguments, argo.Parameter]]]
) -> argo.Arguments:
    parameters, artifacts = _convert_params(args)
    return argo.Arguments(parameters=parameters, artifacts=artifacts)


def get_inputs(
    args: Union[dict[str, str], list[Union[argo.Arguments, argo.Parameter]]]
) -> argo.Inputs:
    parameters, artifacts = _convert_params(args)
    return argo.Inputs(parameters=parameters, artifacts=artifacts)


def get_outputs(
    args: Union[dict[str, str], list[Union[argo.Arguments, argo.Parameter]]]
) -> argo.Outputs:
    parameters, artifacts = _convert_params(args)
    return argo.Outputs(parameters=parameters, artifacts=artifacts)


def sanitize_name(name: str) -> str:
    if name is None:
        return None
    return name.replace("_", "-")


def uuid_short():
    return shortuuid.random(5)
