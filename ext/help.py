import discord
from discord.ext import commands

class Help(commands.MinimalHelpCommand):
	async def send_pages(self):
		destination = self.get_destination()
		for page in self.paginator.pages:
			emby = discord.Embed(description=page, color=discord.Color.blurple())
			await destination.send(embed=emby)