"""Test setup: force fixture mode so tests never touch the network."""

import os

os.environ["OPENFDA_MODE"] = "fixture"
