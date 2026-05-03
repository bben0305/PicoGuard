"""
API 路由模組
"""

from .sensors import router as sensors_router
from .controls import router as controls_router

__all__ = ["sensors_router", "controls_router"]
