import asyncio
import contextlib

import aiohttp
import discord
from discord.errors import HTTPException, InvalidArgument
from discord.ext import commands
from discord.ext.commands import *
from init import Tragedy


class Events(commands.Cog):
	def __init__(self, bot: Tragedy):
		self.bot = bot

	def teardown(self):
		asyncio.run_coroutine_threadsafe(self.session.close)

	@commands.Cog.listener("on_message_delete")
	async def no_snipe__callback(self, message: discord.Message):
		if not self.bot.no_snipe:
			return
		if message.author != self.bot.user:
			return
		if message.nonce == 666666666666666666:
			return
		await message.channel.send("\u200b", delete_after=0.1, nonce=666666666666666666)

	@commands.Cog.listener("on_message_delete")
	async def message_logger__callback(self, message: discord.Message):
		if self.bot.message_logging and message.author != self.bot.user and not message.author.bot and len(message.clean_content) <= 1024:
			_ = aiohttp.ClientSession(loop=self.bot.loop)
			try:
				logger = discord.Webhook.from_url(self.bot.message_logging_webhook, adapter=discord.AsyncWebhookAdapter(session=_))
			except InvalidArgument:
				return
			embed = discord.Embed(color=discord.Color.blurple(), timestamp=message.created_at)
			embed.set_author(name=message.author, icon_url=str(message.author._user.avatar_url) if message.guild else str(message.author.avatar_url))
			if message.guild:
				embed.add_field(name="Guild", value=message.guild.name)
			if not message.guild:
				if isinstance(message.channel, discord.DMChannel):
					embed.add_field(name="DM With", value=message.channel.recipient)
				elif isinstance(message.channel, discord.GroupChannel):
					embed.add_field(name="Group Chat With", value='\n'.join(message.channel.recipients))
					embed.add_field(name="Group Chat Name", value=message.channel.name)
			if message.content:
				embed.add_field(name="Content", value=message.clean_content, inline=False)
			if message.attachments:
				embed.add_field(name="Attachments", value=('\n'.join([attachment.proxy_url for attachment in message.attachments]) or "None"), inline=False)
			await logger.send(username="Tragedy Selfbot", embed=embed)
			await _.close()

	@commands.Cog.listener("on_group_remove")
	async def no_leave__callback(self, channel: discord.GroupChannel, user: discord.User):
		with contextlib.suppress(KeyError):
			if not self.bot.no_leave_chats[channel.id]:
				return
			if user in self.bot.no_leave_chats[channel.id]:
				with contextlib.suppress(HTTPException):
					await channel.add_recipients(user)

def setup(bot):
	bot.add_cog(Events(bot))
