from collections import defaultdict
from typing import List, DefaultDict
import discord
from discord.ext import commands
from redbot.core import Config
from redbot.core.utils.chat_formatting import box

from .squad import Squad
from .utils import Rank

class R6Squads:

    def __init__(self):
        self.conf: Config = Config.get_conf(self, identifier=0x190a88e5, force_registration=True)
        self.conf.register_guild(rank_diff=1)
        self.squads: DefaultDict[discord.Guild, List[Squad]] = defaultdict(lambda: [])

    @commands.command()
    async def squad(self, ctx: commands.Context, *, rank: Rank):
        """Find a squad.

        Example usage:
          [p]squad platinum 3
          [p]squad diamond
          [p]squad copper 1
          [p]squad unranked
        """
        cur_squad = self.get_squad(ctx.author)
        if cur_squad is not None:
            await ctx.send("You are already in a squad. Use `{0}leavesquad` to leave it. "
                           "Use `{0}viewsquad` to see who is in your current squad."
                           "".format(ctx.prefix))
            return
        rank_diff = await self.conf.guild(ctx.guild).rank_diff()
        for squad in self.squads[ctx.guild]:
            if squad.is_full():
                continue
            if squad.in_range(rank, rank_diff):
                squad.add_member(ctx.author)
                await ctx.send("A squad has been found! The squad now consists of:\n"
                               + box(squad.get_name_list()))
                break
        else:
            await ctx.send("Could not find an existing squad to place you in. "
                           "A new squad will be created for you.")
            self.create_squad(rank, ctx.author)

    @commands.command()
    async def leavesquad(self, ctx: commands.Context):
        """Leave your current squad."""
        squad = self.get_squad(ctx.author)
        if squad is None:
            await ctx.send("You are not in a squad yet.")
            return
        squad.remove_member(ctx.author)
        if not squad.members:
            self.delete_squad(squad)
            await ctx.send("You have left your squad. Since it is now empty, the squad has been "
                           "deleted.")
            return
        await ctx.send("You have left your squad.")

    @commands.command()
    async def viewsquad(self, ctx: commands.Context):
        """View your current squad."""
        squad = self.get_squad(ctx.author)
        if squad is None:
            await ctx.send("You are not in a squad yet.")
            return
        await ctx.send("Your current squad consists of:\n" + box(squad.get_name_list()))

    def get_squad(self, member: discord.Member) -> Squad:
        for squad in self.squads[member.guild]:
            if member in squad.members:
                return squad

    def create_squad(self, median_rank: Rank, first_member: discord.Member):
        squad = Squad(median_rank, [first_member])
        self.squads[first_member.guild].append(squad)

    def delete_squad(self, squad: Squad):
        self.squads[squad.guild].remove(squad)
