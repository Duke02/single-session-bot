from discord import commands


class SingleSessionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ss_join_queue(self, ctx):
        """Adds the calling user to the SingleSession Queue"""
