# -*- coding: utf-8 -*-

import asyncio
import json
import sqlite3
import typing

import aiohttp
import discord
from discord.ext import commands
from ext.procedures import *
from init import Tragedy


class Config(commands.Cog):
	def __init__(self, bot: Tragedy):
		self.bot = bot
		self.session = aiohttp.ClientSession(loop=self.bot.loop)

	def teardown(self):
		asyncio.run_coroutine_threadsafe(self.session.close(), self.bot.loop)

	@commands.command(name="deldelay")
	async def delete_delay(self, ctx: commands.Context, *, delay: typing.Optional[typing.Union[int, float]]):
		if not delay:
			self.bot.set_environment("delete_message_delay", None)
			await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Removed message deletion delay."))
		elif delay:
			self.bot.set_environment("delete_message_delay", float(delay))
			await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Set message deletion delay to `{0}`.".format(float(delay))), delete_after=float(delay))

	@commands.group(name="log", invoke_without_command=True)
	async def message_logging(self, ctx: commands.Context):
		await ctx.send_help(ctx.command)

	@message_logging.command(name="on")
	async def message_logging_on(self, ctx: commands.Context):
		self.bot.set_environment("message_logging", True)
		self.bot.set_environment("message_logging_webhook", None)
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Set message logging on.\nPlease configure your webhook (`log hook`)."), delete_after=self.bot.delete_delay)
	
	@message_logging.command(name="off")
	async def message_logging_off(self, ctx: commands.Context):
		self.bot.set_environment("message_logging", False)
		self.bot.set_environment("message_logging_webhook", None)
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Set message logging off."), delete_after=self.bot.delete_delay)

	@message_logging.command(name="hook")
	async def message_logging_webhook(self, ctx: commands.Context, *, webhook: typing.Optional[str]):
		if not webhook:
			log_channel = discord.utils.get(self.bot.log_guild.text_channels, name="message-logs")
			throw_ = discord.utils.get(await log_channel.webhooks(), name="Tragedy Message Logs")
			webhook = ((await log_channel.create_webhook(name="Tragedy Message Logs")).url) if throw_ is None else throw_.url
		self.bot.set_environment("message_logging_webhook", webhook)
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Set message logging webhook."), delete_after=self.bot.delete_delay)

	@commands.group(name="nosnipe", invoke_without_command=True)
	async def no_snipe(self, ctx: commands.Context):
		await ctx.send_help(ctx.command)

	@no_snipe.command(name="on")
	async def no_snipe_on(self, ctx: commands.Context):
		self.bot.set_environment("no_snipe", True)
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Set no-snipe on."), delete_after=self.bot.delete_delay)
	
	@no_snipe.command(name="off")
	async def no_snipe_off(self, ctx: commands.Context):
		self.bot.set_environment("no_snipe", False)
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Set no-snipe off."), delete_after=self.bot.delete_delay)

	@commands.group(description="Configure API keys", invoke_without_command=True)
	async def setkey(self, ctx: commands.Context):
		await ctx.send_help(ctx.command)

	@setkey.command(description="Set leakcheck.net paid API key")
	async def leakcheck(self, ctx: commands.Context, *, key: typing.Optional[str]):
		if not key:
			self.bot.set_environment("leakcheck_api_key", None)
			await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Removed LeakCheck API key."), delete_after=self.bot.delete_delay)
		elif key:
			await ctx.message.edit(content="setkey leakcheck [REDACTED]")
			await ctx.message.edit(content="setkey leakcheck `[REDACTED]`")
			async with await self.session.get("https://leakcheck.net/api?key={0}&check=valid&type=login".format(key)) as response:
				data = json.loads(await response.text())
				if not data.get("success"):
					return await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Error setting LeakCheck API key. (`{0}`)".format(data.get('error'))), delete_after=self.bot.delete_delay)
			self.bot.set_environment("leakcheck_api_key", key)
			await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Set LeakCheck API key."), delete_after=self.bot.delete_delay)

	@commands.group(description="View prefixes", invoke_without_command=True)
	async def prefix(self, ctx: commands.Context):
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Prefixes", description=join_iter(self.bot.custom_prefix(None, None), '`\n`', '`')), delete_after=self.bot.delete_delay)

	@prefix.command(description="Add new prefix")
	async def add(self, ctx: commands.Context, *, prefix: str):
		cursor = self.bot.db.cursor()
		try:
			cursor.execute("INSERT INTO prefixes (prefix) VALUES (?)", (prefix))
			self.bot.db.commit()
		except sqlite3.InterfaceError:
			return await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="`{0}` is already a prefix.".format(prefix)), delete_after=self.bot.delete_delay)
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="`{0}` has been added as a prefix.".format(prefix)), delete_after=self.bot.delete_delay)

	@prefix.command(description="Remove a prefix")
	async def remove(self, ctx: commands.Context, *, prefix: str):
		cursor = self.bot.db.cursor()
		try:
			cursor.execute("DELETE FROM prefixes WHERE prefix=?", (prefix))
			self.bot.db.commit()
		except sqlite3.InterfaceError:
			return await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="`{0}` is not a prefix.".format(prefix)), delete_after=self.bot.delete_delay)
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="`{0}` has been removed from prefixes.".format(prefix)), delete_after=self.bot.delete_delay)

def setup(bot):
	bot.add_cog(Config(bot))
