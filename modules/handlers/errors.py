import discord
from discord.ext import commands
from discord.ext.commands import *


class Errors(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx: commands.Context, error):
		if isinstance(error, CommandNotFound):
			return
		elif isinstance(error, MissingPermissions):
			embed = discord.Embed(title="Oops !", description="You need `{0}` permissions for that".format(' '.join(error.missing_permissions[0].split('_')).title()), color=discord.Color.blurple())
			await ctx.reply(embed=embed)
		elif isinstance(error, CheckFailure):
			embed = discord.Embed(title="Oops !", description="You cannot do that, you silly goose", color=discord.Color.blurple())
			await ctx.reply(embed=embed)
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send_help(ctx.command)

def setup(bot):
	bot.add_cog(Errors(bot))
