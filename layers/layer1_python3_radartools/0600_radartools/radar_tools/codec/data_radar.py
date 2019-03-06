#!/bin/env python
# -*- coding: utf-8 -*-

import logging


log = logging.getLogger()


class DataRadar:

    def __init__(self):
        self.common_characteristics = {}
        self.vue = None
        self.pixmaps = []
        self.pixmaps_characteristics = []
        self.catch_all = []
