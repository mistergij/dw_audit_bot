"""Sets up optimizations for event loop and imports necessary modules."""
import asyncio
import os

if os.name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
