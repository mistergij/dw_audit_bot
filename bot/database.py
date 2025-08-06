"""Defines a database class for variable storage.
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

from dataclasses import dataclass

import aiosqlite


@dataclass
class Database:
    """Class to keep track of Kensa's SQLite databases"""

    connection: aiosqlite.Connection = None
    earliest_audit: float = None
    latest_audit: float = None
