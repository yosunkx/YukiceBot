import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    print('You can invite the bot by using the following url: ' + discord.utils.oauth_url(bot.user.id))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f'Received message: {message.content}')

    # Check if the message is a command
    ctx = await bot.get_context(message)
    is_command = ctx.valid

    print(f'This message is a bot command: {is_command}')

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

token = 'MTA5NzM0MTc0NzQ1OTI3Mjg0NQ.Gst0oI.NrP5b8dn9gPKbi-c8UzyKfTjjt4K9Z6sP7aBhQ'
bot.run(token)