# -*- coding: utf-8 -*-

"""
ZJUMilCubes API 客户端
提供与 ZJUMilCubes 平台简单交互的功能
"""

from .api import MilCubesSession, Project, ProjectCollection

__version__ = "0.1.1"
__all__ = ["MilCubesSession", "Project", "ProjectCollection"]