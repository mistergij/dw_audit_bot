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
import crescent
from sqlalchemy import create_engine
import hikari

from bot.constants import (
    database,
    DEV_IDS,
    Plugin,
    EARLIEST_AUDIT_PATH,
    MAIN_DATABASE_PATH,
)
from bot.errors import InsufficientPrivilegesError

plugin = Plugin()
database_commands = crescent.Group("database")


@plugin.include
@crescent.event
async def start_database(event: hikari.StartingEvent) -> None:
    database.connection = await aiosqlite.connect(MAIN_DATABASE_PATH)
    database.engine = create_engine(f"sqlite:///{MAIN_DATABASE_PATH}")
    with open(EARLIEST_AUDIT_PATH, "r") as file:
        try:
            database.earliest_audit = float(file.read())
        except ValueError:
            pass
    await database.connection.executescript(
        """BEGIN;
                CREATE VIEW IF NOT EXISTS train_no_xp AS SELECT message_id, message_timestamp, remaining_dtd, old_purse, new_purse, lifestyle, injuries, dtd_type, user_id, user_name, char_name FROM train;
                DROP VIEW IF EXISTS raw_all;
                CREATE VIEW raw_all AS SELECT * FROM guild UNION SELECT * FROM business UNION SELECT * FROM ptw UNION SELECT * FROM hrw UNION SELECT * FROM odd UNION SELECT * FROM train_no_xp;
                DROP VIEW IF EXISTS raw_xp_appended;
                CREATE VIEW raw_xp_appended AS SELECT raw_all.*, ifnull(train.xp_gained, 0) as xp_gained from raw_all left join train USING (message_id);
                CREATE VIRTUAL TABLE IF NOT EXISTS filtered_all USING FTS5(message_id, dtd_type, user_id, char_name, content=raw_xp_appended, content_rowid=message_id);
                INSERT INTO filtered_all(filtered_all) VALUES('rebuild');
                CREATE TRIGGER IF NOT EXISTS filtered_all_ai_guild AFTER INSERT ON guild BEGIN 
                    INSERT INTO filtered_all(rowid, dtd_type, user_id, char_name) VALUES (new.message_id, new.dtd_type, new.user_id, new.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ai_business AFTER INSERT ON business BEGIN 
                    INSERT INTO filtered_all(rowid, dtd_type, user_id, char_name) VALUES (new.message_id, new.dtd_type, new.user_id, new.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ai_ptw AFTER INSERT ON ptw BEGIN 
                    INSERT INTO filtered_all(rowid, dtd_type, user_id, char_name) VALUES (new.message_id, new.dtd_type, new.user_id, new.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ai_hrw AFTER INSERT ON hrw BEGIN 
                    INSERT INTO filtered_all(rowid, dtd_type, user_id, char_name) VALUES (new.message_id, new.dtd_type, new.user_id, new.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ai_odd AFTER INSERT ON odd BEGIN 
                    INSERT INTO filtered_all(rowid, dtd_type, user_id, char_name) VALUES (new.message_id, new.dtd_type, new.user_id, new.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ai_train AFTER INSERT ON train BEGIN 
                    INSERT INTO filtered_all(rowid, dtd_type, user_id, char_name) VALUES (new.message_id, new.dtd_type, new.user_id, new.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ad_guild AFTER DELETE ON guild BEGIN 
                    INSERT INTO filtered_all(filtered_all, rowid, dtd_type, user_id, char_name) VALUES ('delete', old.message_id, old.dtd_type, old.user_id, old.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ad_business AFTER DELETE ON business BEGIN 
                    INSERT INTO filtered_all(filtered_all, rowid, dtd_type, user_id, char_name) VALUES ('delete', old.message_id, old.dtd_type, old.user_id, old.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ad_ptw AFTER DELETE ON ptw BEGIN 
                    INSERT INTO filtered_all(filtered_all, rowid, dtd_type, user_id, char_name) VALUES ('delete', old.message_id, old.dtd_type, old.user_id, old.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ad_hrw AFTER DELETE ON hrw BEGIN 
                    INSERT INTO filtered_all(filtered_all, rowid, dtd_type, user_id, char_name) VALUES ('delete', old.message_id, old.dtd_type, old.user_id, old.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ad_odd AFTER DELETE ON odd BEGIN 
                    INSERT INTO filtered_all(filtered_all, rowid, dtd_type, user_id, char_name) VALUES ('delete', old.message_id, old.dtd_type, old.user_id, old.char_name);
                END;
                CREATE TRIGGER IF NOT EXISTS filtered_all_ad_train AFTER DELETE ON train BEGIN 
                    INSERT INTO filtered_all(filtered_all, rowid, dtd_type, user_id, char_name) VALUES ('delete', old.message_id, old.dtd_type, old.user_id, old.char_name);
                END;
            COMMIT;"""
    )


@plugin.include
@crescent.event
async def close_database(event: hikari.StoppingEvent) -> None:
    await database.connection.commit()
    await database.connection.close()
    with open(EARLIEST_AUDIT_PATH, "w") as file:
        file.write(str(database.earliest_audit))


@plugin.include
@database_commands.child
@crescent.command(description="Creates a DTD table with the given name", name="create_database")
class CreateDatabase:
    table_name = crescent.option(str, description="The name of the table to create")

    async def callback(self, ctx: crescent.Context) -> None:
        if ctx.user.mention not in DEV_IDS:
            raise InsufficientPrivilegesError("Insufficient Permissions!")

        await database.connection.execute(
            """CREATE TABLE IF NOT EXISTS %s(
                    message_id INTEGER,
                    message_timestamp REAL,
                    remaining_dtd INTEGER,
                    old_purse REAL,
                    new_purse REAL,
                    lifestyle TEXT,
                    injuries TEXT,
                    dtd_type TEXT,
                    user_id INTEGER,
                    user_name TEXT,
                    char_name TEXT,
                    PRIMARY KEY(message_id DESC)
            );"""
            % f"'{self.table_name.replace("'", "''")}'"
        )
        await ctx.respond("Database created.")


# noinspection PyTypeChecker
@plugin.include
@database_commands.child
@crescent.command(description="Resets latest audit information")
async def reset_latest_audit_info(ctx: crescent.Context) -> None:
    if ctx.user.mention not in DEV_IDS:
        raise InsufficientPrivilegesError("Insufficient Permissions!")
    database.earliest_audit = None
    await ctx.respond("Reset Earliest Audit Info!")


@plugin.include
@database_commands.child
@crescent.command(
    name="query_database",
    description="Sends an SQL query to the database for debugging purposes",
)
class QueryDatabase:
    query = crescent.option(str, "The query to pass to the table")

    async def callback(self, ctx: crescent.Context) -> None:
        if ctx.user.mention not in DEV_IDS:
            raise InsufficientPrivilegesError("Insufficient Permissions!")
        async with aiosqlite.connect(MAIN_DATABASE_PATH) as c:
            async with c.execute(self.query) as cursor:
                result = await cursor.fetchall()
        await ctx.respond(result)


@plugin.include
@crescent.catch_command(InsufficientPrivilegesError)
async def catch_permission_error(exc: InsufficientPrivilegesError, ctx: crescent.Context) -> None:
    await ctx.respond(exc)
