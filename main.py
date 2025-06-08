import asyncio
import os

import hikari
import lightbulb

if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
