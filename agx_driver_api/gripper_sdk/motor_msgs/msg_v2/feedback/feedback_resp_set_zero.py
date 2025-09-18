#!/usr/bin/env python3
# -*-coding:utf8-*-
import math
from typing_extensions import (
    Literal,
)
class FeedbackRespSetZero:
    def __init__(self, 
                 zero_val: int = 0,
                 save_flash: int = 0,
                 ):
        self.zero_val = zero_val
        self.save_flash = save_flash

    def __str__(self):
        return (f"(\n"
                f"  zero_val: {self.zero_val}\n"
                f"  save_flash: {self.save_flash}\n"
                f")")

    def __repr__(self):
        return self.__str__()
