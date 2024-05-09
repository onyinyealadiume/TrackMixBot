import os
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from keep_alive import keep_alive
from database import create_connection, insert_user, search_songs
import yt_dlp
TOKEN = os.environ['TOKEN']

intents = discord.Intents.all()
TOKEN = os.environ['TOKEN']

client = commands.Bot(command_prefix='!', intents=intents)
@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))


@client.command()
async def dl(ctx, arg1):
    discord_id = ctx.message.author.id  # Discord user ID
    username = ctx.message.author.name  # Get the username from the context
    await ctx.message.channel.send('Processing mp3...')
    
    # Function to get the video title
    def get_video_title(url):
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
                return info_dict.get('title', None)
            except Exception as e:
                print(f"Error fetching video title: {e}")
                return None

    # Fetch the title
    title = get_video_title(arg1)
    if title is None:
        await ctx.send("Failed to fetch the video title. Check the URL or try again.")
        return 
    
    # Assuming downLoad also handles the conversion and returns the path to the mp3 file
    file = downLoad(arg1)
    if file is None:
        await ctx.message.channel.send("Failed to download and convert the video.")
        return
    
    # Connect to the database and insert song details
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            user_id = insert_user(conn, discord_id, username)  # Ensure the user is in the database
            cursor.execute('''INSERT INTO songs (title, user_id, link, pathToMp3, convertedAt) 
                              VALUES (?, ?, ?, ?, datetime('now'))''', 
                           (title, user_id, arg1, file))
            conn.commit()
            msg = f'Hey {ctx.message.author.mention}! Your mp3 "{title}" has finished processing 😊! Download and enjoy!'
            await ctx.message.channel.send(content=msg, file=discord.File(file))
        except Exception as e:
            print("Error when inserting into the database:", e)
            await ctx.message.channel.send('There was an error processing your request.')
        finally:
            cursor.close()
            conn.close()
    else:
        await ctx.message.channel.send('Failed to connect to the database.')

    deleteFile(file)


@client.command()
async def search(ctx, *, keyword):
    await ctx.message.channel.send('Searching for songs...')
    results = search_songs(keyword)
    if results:
        response = "Here are the songs I found:\n" + '\n'.join([f"{idx + 1}. {title}" for idx, title in enumerate(results)])
        await ctx.message.channel.send(response)
    else:
        await ctx.message.channel.send("No songs found matching your query.")   
   
@client.command()
async def h(ctx):
  embed = discord.Embed(title='Commands', description='These are all the commands this botuses. \n\n *Note: This bot ONLY works with youtube videos for now*\n\n', color=0xFF5733)
  
  embed.add_field(name='`!h`', value="\n Help command returns info on this bot and other commands.", inline=False)

  embed.add_field(name='`!dl <youtube link>`', value="\n Download command that converts youtube link to a downloadable mp3. \n\nEx: `!dl https://www.youtube.com/watch?v=pNeZjNgvu38`", inline=False)

  embed.add_field(name='`!search <keyword>`', value="\n Search command that looks for songs in the database that match the keyword in their title. \n\nEx: `!search love`", inline=False)

  await ctx.message.channel.send(embed = embed)


@client.event
async def on_guild_join(guild):
    general = guild.text_channels[0]
    if general and general.permissions_for(guild.me).send_messages:
        embed=discord.Embed(title="**== *Thanks For Adding Me!* ==**", description=f"""
        Hi!! I'm WindysCorner 😄! I'm a discord bot that lets you convert Youtube videos to mp3s! Thanks for adding me to {guild.name}! \n  
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