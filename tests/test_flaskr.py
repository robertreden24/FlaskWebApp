import os
import tempfile

import pytest
import sys
def pytest_configure(config):
    import sys
    sys._called_from_test = True

def pytest_unconfigure(config):
    import sys 
    del sys._called_from_test

if hasattr(sys, '_called_from_test'):
    return 'called from within a test run'
else:
    return 'called normally'
