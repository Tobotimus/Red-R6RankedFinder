from datetime import datetime
from typing import List
import discord

from .utils import Rank


class Squad:

    def __init__(self, median_rank: Rank, members: List[discord.Member], *, _id: int=None):
        self.median_rank: Rank = median_rank
        if not members:
            raise ValueError("Must be at least one member to start a squad.")
        self.members: List[discord.Member] = members.copy()
        self.guild: discord.Guild = members[0].guild
        if _id is None:
            self.id = discord.utils.time_snowflake(datetime.now())
        else:
            self.id = _id

    def is_full(self) -> bool:
        return len(self.members) >= 5

    def in_range(self, rank: Rank, rank_diff: int):
        try:
            lower = self.median_rank - rank_diff
        except ValueError:
            lower = Rank.unranked()

        try:
            upper = self.median_rank + rank_diff
        except ValueError:
            upper = Rank.diamond()

        return lower <= rank <= upper

    def get_name_list(self) -> str:
        names = []
        for member in self.members:
            names.append("{0.display_name} ({0})".format(member))
        return "\n".join(names)

    def add_member(self, member: discord.Member):
        if len(self.members) >= 5:
            raise RuntimeError("Squad is full.")
        if member in self.members:
            return False
        self.members.append(member)
        return True

    def remove_member(self, member: discord.Member):
        if member in self.members:
            self.members.remove(member)
            return True
        return False
