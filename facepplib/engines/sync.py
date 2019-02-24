"""
Synchronous blocking engine that processes requests one by one.
"""

import requests

from . import BaseEngine


class SyncEngine(BaseEngine):
    @staticmethod
    def create_session(**params):
        session = requests.Session()

        for param in params:
            setattr(session, param, params[param])

        return session
