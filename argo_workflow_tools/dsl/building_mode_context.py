from contextvars import ContextVar

"""
this context variable keeps the context of the current DAG run ,
making sure that without calling the function in a context of a workflow compilation
the function will run as-is.
"""
dag_building_mode: ContextVar[bool] = ContextVar("dag_building_mode", default=False)
