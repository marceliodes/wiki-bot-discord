import os
import asyncio
from random import choice
import discord
from discord.ext import commands
from dotenv import load_dotenv
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

# Load variables from the .env file into the system environment
load_dotenv()

# Assign the environment variable to a Python variable
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Set up required intents
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read prefix commands

# Prefix before typing command
bot = commands.Bot(command_prefix=">w ", intents=intents, help_command=None)

# Set default language
current_language = "en"
wikipedia.set_lang(current_language)


# Print on terminal when bot is active and change presence to show status
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('>w help'))
    print("Bot in server: {}".format(len(bot.guilds)))
    print("Bot name: {}".format(bot.user.name))


# Command to use search term
@bot.command()
async def search(ctx, *, request: str = None):

    # Load current language for picture
    global current_language

    # Handle missing input gracefully
    if not request:
        wikicontent = "Sorry, there are no search results for ''."
        embed = discord.Embed(title="Wikipedia search results:", color=0xe74c3c, description=wikicontent)
        embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
        await ctx.send(embed=embed)
        return

    try:
        wikicontent = wikipedia.search(request, results=20, suggestion=False)  # Wikipedia search request
        print(wikicontent)
        print(" ".join(wikicontent))

        # If there are no results
        if not wikicontent:
            wikicontent = "Sorry, there are no search results for '{}'.".format(request)
            embed = discord.Embed(title="Wikipedia search results:", color=0xe74c3c, description=wikicontent)
            embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
            await ctx.send(embed=embed)

        # If there are do:
        else:
            embed = discord.Embed(title="Wikipedia search results:", color=0, description="\n".join(wikicontent))
            embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
            await ctx.send(embed=embed)

    # Handle random errors
    except Exception as error:
        error = str(error)
        await ctx.send("Sorry, a random error occurred. Please try again.")
        print(error)


# Command to print wiki page
@bot.command()
async def wiki(ctx, *, request: str = None):

    global current_language

    # Handle missing input gracefully
    if not request:
        NoResultErrorMessage = "Sorry, there are no Wikipedia article with this title. Please try '>search (your request)' to look up Wikipedia article name"
        embed = discord.Embed(title="Not found: ", color=0xe74c3c, description=NoResultErrorMessage)
        embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
        await ctx.send(embed=embed)
        return

    # Checks if the request is valid
    try:
        pagecontent = wikipedia.page(request)
        pagetext = wikipedia.summary(request, sentences=5)

        # Try to get random image from the article to display.
        # If there are no pictures, it wil set it to the default wkikipedia picture
        try:
            if pagecontent.images:
                thumbnail = choice(pagecontent.images)
            else:
                thumbnail = "https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language)
        except Exception:
            thumbnail = "https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language)

        embed = discord.Embed(title=request, color=0, description=pagetext + "\n\n[Read further]({})".format(pagecontent.url))
        embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)

    except wikipedia.DisambiguationError:
        NotSpecificRequestErrorMessage = """Sorry, your search request wasn't specific enough. Please try '>search (your request)'. This will display all wikipedia articles with your search request. You can than copy the correct result and put that in >wiki command."""
        embed = discord.Embed(title="Bad request: ", color=0xe74c3c, description=NotSpecificRequestErrorMessage)
        embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
        await ctx.send(embed=embed)

    except wikipedia.PageError:
        NoResultErrorMessage = "Sorry, there are no Wikipedia article with this title. Please try '>search (your request)' to look up Wikipedia article name"
        embed = discord.Embed(title="Not found: ", color=0xe74c3c, description=NoResultErrorMessage)
        embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
        await ctx.send(embed=embed)

    except Exception:
        RandomErrorMessage = "Sorry, a random error occured"
        embed = discord.Embed(title="Error", color=0xe74c3c, description=RandomErrorMessage)
        embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
        await ctx.send(embed=embed)


# Command to print random page on wiki
@bot.command()
async def random(ctx):

    global current_language

    # Loop until a valid, non-disambiguation article is fetched
    while True:
        try:
            random_article = wikipedia.random(pages=1)
            pagecontent = wikipedia.page(random_article)
            pagetext = wikipedia.summary(random_article, sentences=5)
            break
        except (DisambiguationError, PageError):
            continue

    # Try to set an random image in the article as the thumbnail
    try:
        if pagecontent.images:
            thumbnail = choice(pagecontent.images)
        else:
            thumbnail = "https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language)
    except Exception as error:
        thumbnail = "https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language)
        print("Couldn't load {}".format(thumbnail))

    embed = discord.Embed(title=random_article, color=0, description=pagetext + "\n\n[Read further]({})".format(pagecontent.url))
    embed.set_thumbnail(url=thumbnail)
    await ctx.send(embed=embed)


# Command to print about this bot
@bot.command()
async def about(ctx):

    global current_language

    # Just an about page
    about = "{} is a bot made using [Wikipedia Api](https://wikipedia.readthedocs.io/en/latest/code.html). All articles fall under the [Creative Commons Attribution-ShareAlike License](https://en.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License).".format(bot.user.name)
    embed = discord.Embed(title="About:", color=0, description=about + "\n\n[Wikipedia Official Site](https://en.wikipedia.org/wiki/Main_Page)")
    embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
    await ctx.send(embed=embed)


# Command to see how to use the bot
@bot.command()
async def help(ctx):

    await ctx.send("```List of commands :\n\n>w search 'term' : Search article on wikipedia with the given term\n>w wiki 'term'   : Show the article with the given term\n>w random        : Show random article from wikipedia\n>w about         : Show information about the bot```")


# Checks if the token is correct
if DISCORD_TOKEN:
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("Incorrect token")
else:
    print("DISCORD_TOKEN is missing from .env file!")