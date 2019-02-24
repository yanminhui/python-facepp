"""
Defines engines for processing requests/responses to/from FacePP.
"""

from .base import BaseEngine
from .sync import SyncEngine

DefaultEngine = SyncEngine
