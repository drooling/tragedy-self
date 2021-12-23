# -*- coding: utf-8 -*-

import asyncio
import json
import string
import typing

import aiohttp
import discord
from discord.ext import commands
from ext.procedures import *
from init import Tragedy
from jishaku.codeblocks import codeblock_converter


class Info(commands.Cog):
	def __init__(self, bot: Tragedy):
		self.bot = bot
		self.session = aiohttp.ClientSession(loop=self.bot.loop)
		self.bot.help_command.cog = self
		asyncio.run_coroutine_threadsafe(self.on_cog_load(), self.bot.loop)

	async def on_cog_load(self):
		async with self.session.get('https://raw.githubusercontent.com/IRIS-Team/IRIS/main/data/domains.txt') as request:
			self.email_domains = [x.strip() for x in (await request.text()).splitlines() if len(x.strip()) > 0]

	def _validate_guess(self, email_domain: str, domain: str) -> bool:
		if len(email_domain) != len(domain):
			return False
		positions = []
		[positions.append((position, char)) for position, char in enumerate(email_domain) if char != '*']
		for position, char in positions:
			if domain[position] != char:
				return False
		return True

	def teardown(self):
		asyncio.run_coroutine_threadsafe(self.session.close(), self.bot.loop)

	@commands.command(description="Get password combos exposed in data breaches", aliases=['leaked', 'leaks'])
	async def breaches(self, ctx: commands.Context, *queries):
		if not self.bot.environment("leakcheck_api_key"):
			return await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Please set your LeakCheck API key (`setkey leakcheck`)."), delete_after=self.bot.delete_delay)
		async with await self.session.get("https://leakcheck.net/api?key={0}&check=valid&type=login".format(self.bot.environment("leakcheck_api_key"))) as response:
			data = json.loads(await response.text())
			if not data.get("success"):
				return await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description="Your current LeakCheck API key is invalid, please set a new one (`setkey leakcheck`)."), delete_after=self.bot.delete_delay)
		template = string.Template("${combo} | Last Breach - ${last_breach} | Sources - ${sources}")
		for _query in enumerate(queries, 1):
			combos = set()
			endpoint = "https://leakcheck.net/api/?key={0}&check={1}&type=auto".format(self.bot.environment("leakcheck_api_key"), _query[1])
			async with self.session.get(endpoint, ssl=True) as _response:
				jObj = json.loads(await _response.text())
				try:
					if len(jObj['result']) > 0:
						for _index in jObj['result']:
							vars = {
								"combo": _index['line'],
								"last_breach": _index['last_breach'] or "Not Found",
								"sources": ', '.join(_index['sources']) or "Not Found"
							}
							combos.add(template.safe_substitute(**vars))
						async with self.session.post("https://hastebin.com/documents", data='\n'.join(combos)) as hastebin:
							hasteObj = await hastebin.json()
						description = 'Password combos found in breaches have been put into a hastebin. [Click Here](%s)' % ("https://hastebin.com/{}".format(hasteObj.get('key')))
				except KeyError:
					description = "No Breaches Found."
			embed = discord.Embed(title="Breaches for `{}`".format(_query[1]), description=description, color=discord.Color.green())
			await ctx.send(embed=embed, delete_after=self.bot.delete_delay)

	@commands.command(description="Guess domain of partial email")
	async def guess(self, ctx: commands.Context, *, email: str):
		email = codeblock_converter(email).content
		email_name, email_domain = email.split('@')
		valid_domains = [domain for domain in self.email_domains if self._validate_guess(email_domain, domain) is True]
		if len(valid_domains) == 0:
			return await ctx.reply("No domains found")
		async with self.session.post("https://hastebin.com/documents", data='\n'.join([email_name + '@' + domain for domain in valid_domains])) as hastebin:
			hasteObj = await hastebin.json()
		await ctx.send(embed=discord.Embed(title="Possible Emails", color=discord.Color.green(), description="Possible emails have been compiled into a hastebin. [Click Here](%s)" % ("https://hastebin.com/{0}".format(hasteObj.get('key')))), delete_after=self.bot.delete_delay)

	@commands.command(description="IP lookup")
	async def lookup(self, ctx: commands.Context, *, host: typing.Optional[str]):
		if not aiohttp.helpers.is_ipv4_address(host):
			return await ctx.reply("Invalid IPv4 address", delete_after=5)
		async with self.session.get('http://ip-api.com/json/{0}?fields=20127263'.format(host)) as response:
			jObj = json.loads(await response.text())
		embed = discord.Embed(title="IP Lookup", color=discord.Color.green())
		embed.add_field(name="Continent", value="{0} (**{1}**)".format(jObj.get('continent', 'N/A'), jObj.get('continentCode', 'N/A')), inline=False)
		embed.add_field(name="Country", value="{0} (**{1}**)".format(jObj.get('country', 'N/A'), jObj.get('countryCode', 'N/A')), inline=False)
		embed.add_field(name="Region", value="{0} (**{1}**)".format(jObj.get('regionName', 'N/A'), jObj.get('region', 'N/A')), inline=False)
		embed.add_field(name="City", value=jObj.get('city', 'N/A'), inline=False)
		embed.add_field(name="ISP", value="{0} (**{1}**)".format(jObj.get('isp', 'N/A'), jObj.get('org', 'N/A')), inline=False)
		embed.add_field(name="AS", value=jObj.get('as', 'N/A'), inline=False)
		embed.add_field(name="Reverse DNS", value=jObj.get('reverse', 'N/A'), inline=False)
		embed.add_field(name="Proxy", value=jObj.get('proxy', 'N/A'), inline=False)
		embed.add_field(name="Mobile", value=jObj.get('mobile', 'N/A'), inline=False)
		embed.add_field(name="Hosting", value=jObj.get('hosting', 'N/A'), inline=False)
		await ctx.reply(embed=embed)

	@commands.command(description="Get HTTP status code of website")
	async def status(self, ctx: commands.Context, *, website: str):
		async with self.session.get(website) as status:
			await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Status", description="{0} returned  `{1}`".format(website, status.status)).set_image(url=str("https://http.cat/" + str(status.status))), delete_after=self.bot.delete_delay)

def setup(bot):
	bot.add_cog(Info(bot))
