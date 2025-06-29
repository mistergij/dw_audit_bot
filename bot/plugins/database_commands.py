"""Plugin that contains all database commands for the bot.
Copyright © 2025 Dnd World

This file is part of Kensa.
Kensa is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
later version.

Kensa is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with Kensa. If not, see
<https://www.gnu.org/licenses/>.
"""

import aiosqlite

from bot.utils import *

plugin = Plugin()


@plugin.include
@crescent.command(description="Creates the guild DTD database and corresponding tables")
async def create_guild_database(ctx: crescent.Context):
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as c:
        await c.execute(f'ATTACH DATABASE "{GUILD_DATABASE_PATH}" AS guild;')
        await c.commit()
        for dtd in GUILD_DTD_LIST:
            await c.execute(
                f"""CREATE TABLE IF NOT EXISTS guild.{dtd}(
                        message_id INTEGER,
                        message_timestamp TEXT,
                        remaining_dtd INTEGER,
                        old_purse REAL,
                        new_purse REAL,
                        lifestyle TEXT,
                        injuries TEXT,
                        PRIMARY KEY(message_id DESC)
                );"""
            )
    await ctx.respond("Database created.")
