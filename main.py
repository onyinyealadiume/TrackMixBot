import os
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from keep_alive import keep_alive

TOKEN = os.environ['TOKEN']

client = commands.Bot(command_prefix = '!')


@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))

@client.command()
async def dl(ctx, arg1):
  await ctx.message.channel.send('Processing mp3...')
  file = downLoad(arg1)
  msg = 'Hey {0}! Your mp3 has finished processing 😊! Download and enjoy! \n'.format(ctx.message.author.mention)

  await ctx.message.channel.send(content = msg, file=discord.File(file))

  deleteFile(file)

@client.command()
async def h(ctx):
  embed = discord.Embed(title='Commands', description='These are all the commands Muse Bot uses. \n\n *Note: Muse Bot ONLY works with youtube videos*\n\n', color=0xFF5733)
  
  embed.add_field(name='`!h`', value="\n Help command returns info on Muse Bot and other commands.", inline=False)

  embed.add_field(name='`!dl <youtube link>`', value="\n Download command that converts youtube link to a downloadable mp3. \n\nEx: `!dl https://www.youtube.com/watch?v=pNeZjNgvu38`", inline=False)

  await ctx.message.channel.send(embed = embed)

@client.event
async def on_guild_join(guild):
    general = guild.text_channels[0]
    if general and general.permissions_for(guild.me).send_messages:
        embed=discord.Embed(title="**== *Thanks For Adding Me!* ==**", description=f"""
        Hi!! I'm Muse 😄! I'm a discord bot that lets you convert Youtube videos to mp3s! Thanks for adding me to {guild.name}! \n  
You can use the `!h` command to get started!
        """, color=0xd89522)
        
        embed.set_footer(text="p.s. my creator is SaphaelEternal#3735!")
        await general.send(embed=embed)

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('hello'):
    await message.channel.send('Hello!')  

  await client.process_commands(message)

def downLoad(url):
  filename = None

  ydl_opts = {'format': 'bestaudio',
              'outtmpl': '%(title)s.%(ext)s', 
              'writethumbnail': True, 
              'postprocessors': [
                  {'key': 'FFmpegExtractAudio',
                  'preferredcodec': 'mp3'},
                  {'key': 'EmbedThumbnail'},
                  {'key': 'FFmpegMetadata'}]          
    }

  with YoutubeDL(ydl_opts) as ydl:
     ddl = ydl.extract_info(url, download = True)
     filename = ydl.prepare_filename(ddl).replace('webm', 'mp3')
     
  
  
  return filename

def deleteFile(file):
  if os.path.exists(file):
    os.remove(file)
    print('{} deleted'.format(file))
  else:
    print("The file: {} does not exist".format(file))  


keep_alive()
client.run(os.environ['TOKEN'])