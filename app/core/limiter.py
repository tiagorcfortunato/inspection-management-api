"""
app.core.limiter — Rate Limiting Configuration

Configures SlowAPI rate limiter using the client's IP address.
Applied to auth endpoints to prevent brute-force attacks.
Can be disabled via RATE_LIMIT_ENABLED=false for testing.
"""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() != "false",
)
