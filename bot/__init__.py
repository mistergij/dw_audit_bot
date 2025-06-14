"""Defines optimizations for event loop."""

import asyncio
import os

if os.name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from __main__ import main

__all__ = ["main"]
