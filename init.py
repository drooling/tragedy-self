import asyncio
import contextlib
import itertools
import json
import os
import sqlite3
from typing import Any, Optional, Set, Union

import discord
from discord.enums import Status
from discord.errors import NotFound
from discord.ext import commands

from ext.help import Help

INITIAL_MODULES = [
	"modules.core.fun",
	"modules.core.info",
	"modules.core.config",
	"modules.core.malicious",
	"modules.handlers.errors",
	"modules.handlers.events",
]

class Tragedy(commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix=self.custom_prefix,
			case_insensitive=True,
			strip_after_prefix=True,
			loop=asyncio.get_event_loop(),
			help_command=Help(),
			status=Status.dnd,
			self_bot=True
		)

		exists = os.path.isdir(os.path.join(os.getcwd(), "ignore"))
		if not exists:
			os.mkdir(os.path.join(os.getcwd(), "ignore"))
		self.db = sqlite3.connect("ignore\\environment.db")
		with contextlib.suppress(sqlite3.OperationalError):
			self.db.cursor().execute("CREATE TABLE IF NOT EXISTS prefixes (prefix TEXT NOT NULL UNIQUE)")
			self.db.cursor().execute("CREATE TABLE IF NOT EXISTS config (leakcheck_api_key TEXT DEFAULT NULL, no_snipe BOOLEAN NOT NULL DEFAULT 0, no_embed BOOLEAN NOT NULL DEFAULT 1, nitro_sniper BOOLEAN NOT NULL DEFAULT 1, message_logging BOOLEAN NOT NULL DEFAULT 0, message_logging_webhook VARCHAR(120) DEFAULT NULL, delete_message_delay FLOAT DEFAULT NULL)")

		self.nitro_sniper = bool(self.environment('nitro_sniper'))
		self.no_snipe = bool(self.environment('no_snipe'))
		self.message_logging = bool(self.environment('message_logging'))
		self.message_logging_webhook = str(self.environment('message_logging_webhook'))
		self.no_embed = bool(self.environment('no_embed'))
		self.delete_delay = None
		self.log_guild = None
		self.no_leave_chats = dict()

		for module in INITIAL_MODULES:
			self.load_extension(module)

	async def on_connect(self):
		#
		if not self.environment('delete_message_delay'):
			self.delete_delay = None
		if self.environment('delete_message_delay'):
			self.delete_delay = float(self.environment('delete_message_delay'))
		#
		_ = discord.utils.get(self.guilds, name="Tragedy Logs")
		if not _:
			self.log_guild: discord.Guild = await self.create_guild(name="Tragedy Logs", icon=open("ignore\\assets\\logs.png", 'rb').read(), code="vmJv3V7CBbKJ")
		else:
			self.log_guild: discord.Guild = _
		#

	def environment(self, variable: str) -> Any:
		cursor = self.db.cursor()
		cursor.execute("SELECT {0} FROM config".format(variable))
		_ = cursor.fetchone()
		return tuple(_)[0] if _ else None

	def set_environment(self, variable: str, value: Any) -> None:
		self.db.cursor().execute("UPDATE OR IGNORE config SET {0}=?".format(variable), (value,))
		self.db.cursor().execute("INSERT OR IGNORE INTO config ({0}) VALUES (?)".format(variable), (value,))
		self.db.commit()
		self.refresh_config()

	def refresh_config(self):
		self.nitro_sniper = bool(self.environment('nitro_sniper'))
		self.no_snipe = bool(self.environment('no_snipe'))
		self.message_logging = bool(self.environment('message_logging'))
		self.message_logging_webhook = str(self.environment('message_logging_webhook'))
		self.no_embed = bool(self.environment('no_embed'))
		self.delete_delay = float(self.environment('delete_message_delay'))
		self.log_guild = None

	async def on_command(self, ctx: commands.Context):
		if not self.delete_delay:
			return
		await asyncio.sleep(self.delete_delay)
		with contextlib.suppress(NotFound, discord.Forbidden):
			await ctx.message.delete()

	def custom_prefix(self, bot: Optional[commands.Bot], message: Optional[discord.Message]) -> Union[str, Set[str]]:
		cursor = self.db.cursor()
		cursor.execute("SELECT * FROM prefixes")
		response = cursor.fetchall()
		if not response:
			cursor.execute("INSERT INTO prefixes (prefix) VALUES ('!')")
			self.db.commit()
			return '!'
		return set(itertools.chain(*response))

Tragedy().run(json.load(open('config.json', 'r'))["token"])
