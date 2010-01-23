# -*- coding: utf-8 -*-
"""
CPSC 599 module: src.languages.null

Purpose
=======
 Contains a collection of rules to apply to phonemes.
 
Language
========
 This file applies to no language. It provided to allow developers to quickly
 determine just how effectively their rules work compared to the baseline
 synthesis parameters.
 
Legal
=====
 All code, unless otherwise indicated, is original, and subject to the
 terms of the GPLv3, which is provided in COPYING.
 
 (C) Neil Tallim, 2009
"""
import src.ipa as ipa

NAME = "null"

RULE_FUNCTIONS = (
) #: A collection of all functions to call, in order, to apply this language's rules. 
