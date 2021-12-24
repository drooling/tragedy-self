# -*- coding: utf-8 -*-

import json
import typing

import aiohttp
import discord
from discord.ext import commands
from ext.procedures import *
from init import Tragedy


class Fun(commands.Cog):
	def __init__(self, bot: Tragedy):
		self.bot = bot
		self.session = aiohttp.ClientSession(loop=self.bot.loop)

	@commands.command(description="Get picture of random shiba.")
	async def shiba(self, ctx: commands.Context):
		async with self.session.get("https://shibe.online/api/shibes?count=1&urls=true&httpsUrls=true") as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Random Shiba").set_image(url=jobj[0]), delete_after=self.bot.delete_delay)

	@commands.command(description="Get picture of random fox.")
	async def fox(self, ctx: commands.Context):
		async with self.session.get("https://randomfox.ca/floof/") as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Random Fox").set_image(url=jobj.get("image")), delete_after=self.bot.delete_delay)

	@commands.command(description="Get picture of random dog.")
	async def dog(self, ctx: commands.Context):
		async with self.session.get("https://dog.ceo/api/breeds/image/random") as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Random Dog").set_image(url=jobj.get("message")), delete_after=self.bot.delete_delay)

	@commands.command(description="Get picture of random cat.")
	async def cat(self, ctx: commands.Context):
		async with self.session.get("https://aws.random.cat/meow") as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Random Cat").set_image(url=jobj.get("file")), delete_after=self.bot.delete_delay)

	@commands.command(description="Get a random insult.")
	async def insult(self, ctx: commands.Context):
		async with self.session.get("https://evilinsult.com/generate_insult.php?type=json&lang=en") as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description=jobj.get("insult")).set_footer(text="Just kidding.. maybe..."), delete_after=self.bot.delete_delay)

	@commands.command(description="Get a random dad joke.")
	async def dadjoke(self, ctx: commands.Context):
		async with self.session.get("https://icanhazdadjoke.com/", headers={"Accept": 'application/json'}) as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Random Dad Joke", description=jobj.get("joke")), delete_after=self.bot.delete_delay)

	@commands.command(description="Get a random Chuck Norris joke.")
	async def chuck(self, ctx: commands.Context):
		async with self.session.get("https://api.chucknorris.io/jokes/random") as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Random Chuck Norris Joke", description=jobj.get("value")), delete_after=self.bot.delete_delay)

	@commands.command(description="Get a random Kanye West quote.")
	async def kanye(self, ctx: commands.Context):
		async with self.session.get("https://api.kanye.rest/") as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Random Kanye West Quote", description=jobj.get("quote")), delete_after=self.bot.delete_delay)

	@commands.command(description="Get a random piece of advice.")
	async def advice(self, ctx: commands.Context):
		async with self.session.get("https://api.adviceslip.com/advice") as response:
			jobj = json.loads(await response.text())
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Random Piece of Advice", description=jobj.get("slip").get("advice")), delete_after=self.bot.delete_delay)

def setup(bot):
	bot.add_cog(Fun(bot))
