from enum import IntEnum
from typing import Union, Sequence
from discord.ext import commands


class MajorRank(IntEnum):
    UNRANKED = 0
    COPPER = 1
    BRONZE = 2
    SILVER = 3
    GOLD = 4
    PLATINUM = 5
    DIAMOND = 6

    def needs_minor(self) -> bool:
        """Returns ``True`` if this major rank requires a minor rank."""
        return self not in (self.UNRANKED, self.DIAMOND)

    def minor_range(self) -> Sequence[int]:
        if self in (self.UNRANKED, self.DIAMOND):
            return [0]
        if self == self.PLATINUM:
            return range(1, 4)
        else:
            return range(1, 5)


class BadRankArgument(commands.BadArgument):
    """Invalid rank passed."""
    pass


class Rank:

    def __init__(self, major: MajorRank, minor: int):
        self.major: MajorRank = major
        self.minor: int = minor

    def __len__(self) -> int:
        return self.magnitude

    def __add__(self, other: Union["Rank", int]) -> "Rank":
        new_magnitude = len(self) + _ensure_int(other)
        return self.from_magnitude(new_magnitude)

    def __sub__(self, other: Union["Rank", int]) -> "Rank":
        new_magnitude = len(self) - _ensure_int(other)
        return self.from_magnitude(new_magnitude)

    def __lt__(self, other: Union["Rank", int]) -> bool:
        return len(self) < _ensure_int(other)

    def __le__(self, other: Union["Rank", int]) -> bool:
        return self < other or self == other

    def __gt__(self, other: Union["Rank", int]) -> bool:
        return len(self) > _ensure_int(other)

    def __ge__(self, other: Union["Rank", int]) -> bool:
        return self > other or self == other

    def __eq__(self, other: Union["Rank", int]) -> bool:
        return len(self) == _ensure_int(other)

    @property
    def magnitude(self) -> int:
        ret = 0
        for major in MajorRank:
            for minor in major.minor_range():
                if major == self.major and minor == self.minor:
                    return ret
                ret += 1

    @classmethod
    def unranked(cls):
        return cls(MajorRank.UNRANKED, 0)

    @classmethod
    def diamond(cls):
        return cls(MajorRank.DIAMOND, 0)

    @classmethod
    def from_magnitude(cls, magnitude: int) -> "Rank":
        cur = 0
        for major in MajorRank:
            for minor in major.minor_range():
                if cur == magnitude:
                    return cls(major, minor)
                cur += 1
        else:
            raise ValueError("No rank exists for magnitude {}".format(magnitude))

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> "Rank":
        args = argument.split()
        if len(args) > 2:
            raise commands.BadArgument("Rank can only be two words.")
        if len(args) < 2:
            args += (0,)
        major, minor = args
        try:
            major: MajorRank = getattr(MajorRank, major.upper())
        except AttributeError:
            raise BadRankArgument("Invalid major rank {}.".format(major))
        try:
            minor: int = int(minor)
        except ValueError:
            raise BadRankArgument("Minor rank must be a number, not {}.".format(minor))
        rank_name = major.name.capitalize()
        if major.needs_minor() and minor not in major.minor_range():
            #  minor rank was illegally given/ omitted
            raise BadRankArgument("Major rank '{0}' needs a minor rank between {1[0]} and {1[-1]}"
                                  "".format(rank_name, major.minor_range()))
        elif not major.needs_minor() and minor != 0:
            raise BadRankArgument("Major rank '{0}' does not need a minor rank.".format(rank_name))
        return cls(major, minor)


def _ensure_int(rank: Union[Rank, int]):
    if isinstance(rank, Rank):
        return len(rank)
    return rank
