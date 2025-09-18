#!/usr/bin/env python3
# -*-coding:utf8-*-

from enum import Enum, auto

class ApiVersion(Enum):
    API_VERSION_0_0_1 = '0.0.1'
    API_CURRENT_VERSION = API_VERSION_0_0_1
    API_VERSION_UNKNOWN = 'unknown'
    def __str__(self):
        return f"{self.name} ({self.value})"
    def __repr__(self):
        return f"{self.name}: {self.value}"