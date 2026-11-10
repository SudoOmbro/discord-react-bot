import random
import discord
import urllib3
import wikipedia
import re
import qrcode
import io
import os


from asyncio import sleep
from discord.ext import commands
from AI.chatgpt import ChatGPTAPI, build_messages, GPTAPIError
from bestemmia import generate_bestemmia
from markov.markov_chains import Generator
from PIL import Image, ImageFilter
from dotenv import load_dotenv

from utils.functions import load_words_list

# Intents are required to access certain message data
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

load_dotenv()
AI_TOKEN: str = os.getenv("AI_TOKEN")
BOT_TOKEN: str = os.getenv("BOT_TOKEN")

WIKIPEDIA_REGEX = r"\"(.+)\""

ai = ChatGPTAPI(AI_TOKEN, "gpt-4o-mini")

BOT_TRIGGERS = ["totti", "france"]
RANT_TOPICS = load_words_list("rant_topics")

LAST_MESSAGES: list[dict] = []

SETTINGS: dict = {
    "language": "dialetto romano",
    "character": "Sei Francesco Totti, noto calciatore italiano",
    "extra": "League of Legends e' una merda",
    "directive": "insult people",
    "ire": "3",
    "voices": "Senti un bisbiglio provenire dal muro: "
}

BESTEMMIA_GENERATOR: Generator = Generator()
BESTEMMIA_GENERATOR.ingest_dataset("bestemmie_sample")

DANTE_GENERATOR: Generator = Generator()
DANTE_GENERATOR.ingest_dataset("dante", eol_sequence="\n\n")


def get_request(url) -> str:
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    print(f"Status: {response.status}")
    print("Response Data:")
    return response.data.decode('utf-8')


def search_wikipedia(query: str, lang='en') -> str:
    try:
        wikipedia.set_lang(lang)
        summary = wikipedia.summary(query, sentences=3)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        print("The search term is ambiguous. Here are some possible options:")
        print(e.options)  
    except wikipedia.exceptions.PageError:
        print("No Wikipedia page found for the given search term.")
    except Exception as e:
        print("An error occurred:", e)
    return ""


def string_contains_bot_trigger(string: str) -> bool:
    for trigger in BOT_TRIGGERS:
        if trigger in string.lower():
            return True
    return False


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Calcio"))
    # await send_schizo_message()
    # while True:
    #     interval: int = random.randint(800, 4200)
    #     print(f"Next schizo message in {interval / 60:.2f} minutes.")
    #     await asyncio.sleep(interval)
    #     send_schizo_message()


async def send_schizo_message():
    channel = bot.get_channel(691282426051297353)
    await channel.send("..." + ai.create_completion(build_system_messages() + build_messages("user", SETTINGS["voices"] + random.choice(RANT_TOPICS))), tts=True)


@bot.command(brief="Play music")
async def play(ctx):
    guild = ctx.guild
    for channel in guild.voice_channels:
        if len(channel.members) > 0:
            source = discord.FFmpegPCMAudio("test.mp3")
            if guild.voice_client is None:
                vc = await channel.connect()
                print(f"Connected to {channel.name} in {guild.name}.")
            else:
                vc = guild.voice_client
            vc.play(source, after=lambda e: print("Playback finished:", e))
            # await vc.disconnect()
            return
    


@bot.command(brief="Override AI settings (this might lead to rampancy)")
async def override(ctx, what: str, value: str):
    if what not in SETTINGS:
        await ctx.send(f"Could not override {what}: Not a setting")
    SETTINGS[what] = value
    await ctx.send(f"Overriden '{what}' to '{value}'")


@bot.command(brief="SPAM EVERYONE")
async def messaggini(ctx, duration_str: str):
    duration: int = int(duration_str)
    for i in range(duration):
        await ctx.send("SPAM @everyone", tts=True)
        await sleep(random.randint(1, 5))


@bot.command(brief="porcodio")
async def bestemmia(ctx: commands.Context, *args):
    amount: int = 1
    use_tts: bool = False
    if len(args) >= 1:
        amount = int(args[0])
    if len(args) >= 2:
        use_tts = (args[1] == "y")
    if amount > 40:
        await ctx.send("Ao anche meno!")
        return
    try:
        await ctx.send("\n".join([generate_bestemmia(iterations=int(random.randint(1, 1000) % int(SETTINGS["ire"]))) for i in range(amount)]), tts=use_tts)
    except discord.HTTPException as e:
        await ctx.send("Ao nun me fa generare troppe bestemmie che altrimenti er papa muore!")
        print(e)


@bot.command(brief="porcodio 2.0")
async def bestemmia2(ctx: commands.Context, first_word: str):
    words: list[str] = [first_word]
    while True:
        word = BESTEMMIA_GENERATOR.generate_next_word(words)
        words.append(word)
        if word == "\n":
            break
    await ctx.send(" ".join(words))


@bot.command(brief="nel mezzo del cammin")
async def dante(ctx: commands.Context, first_word: str):
    words: list[str] = [first_word]
    while True:
        word = DANTE_GENERATOR.generate_next_word(words)
        words.append(word)
        if word == "\n":
            break
        if len(words) > 200:
            break
    await ctx.send(" ".join(words))


@bot.command(brief="Generate art from an infamous visage")
async def donzelli(ctx: commands.Context, *args):
    amount: int = 20
    if len(args) >= 1:
        amount = int(args[0])
    if amount > 50:
        await ctx.send("Ao anche meno!")
        return
    byteIO = io.BytesIO()
    img = Image.open("donzelli.png")
    for i in range(amount):
        img = random.choice([
            lambda image: image.filter(filter=ImageFilter.BLUR),
            lambda image: image.filter(filter=ImageFilter.CONTOUR),
            lambda image: image.filter(filter=ImageFilter.DETAIL),
            lambda image: image.filter(filter=ImageFilter.EDGE_ENHANCE),
            lambda image: image.filter(filter=ImageFilter.EMBOSS),
            lambda image: image.filter(filter=ImageFilter.SMOOTH)
        ])(img)
    img.save(byteIO, format='PNG')
    byteIO.seek(0)
    await ctx.send(file=discord.File(byteIO, filename="data.png"))


@bot.command(brief="create a qr code with the given data")
async def makeqr(ctx: commands.Context, data: str):
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    byteIO = io.BytesIO()
    img.save(byteIO, format='PNG')
    byteIO.seek(0)
    await ctx.send(file=discord.File(byteIO, filename="data.png"))


@bot.command(brief="Check AI rampancy")
async def rampancy(ctx: commands.Context):
    letters: int = 0
    for message in LAST_MESSAGES:
        letters += len(message["content"])
    await ctx.send(f"AI rampancy: {letters / 500:.2f}%")


def build_system_messages() -> list[dict]:
    return build_messages(
        "system", 
        SETTINGS["character"], 
        f"Only speak in {SETTINGS["language"]} and {SETTINGS["directive"]}",
        SETTINGS["extra"]
    )


@bot.event
async def on_message(message):
    if message.author == bot.user:
        # Avoid the bot reacting to its own messages
        return
    # add message to messages list
    user_message = build_messages("user", f"{message.author}: " + message.content)
    LAST_MESSAGES.extend(user_message)
    # remove old messages from list
    while len(LAST_MESSAGES) > 20:
        del LAST_MESSAGES[0]
    # process message
    try:
        # if one of the triggers isn't in the message then stop
        if not string_contains_bot_trigger(message.content):
            await bot.process_commands(message)
            if random.random() <= 0.95:
                return
        # if the message has one of the triggers then engage AI
        await message.add_reaction("👀")
        messages = build_system_messages() + LAST_MESSAGES + user_message
        # if the message has quotes somewhere then search that on wikipedia
        match = re.search(WIKIPEDIA_REGEX, message.content)
        if match:
            print(f"Adding Wikipedia context for search: {match.group(1)}")
            wikipedia_result: str = search_wikipedia(match.group(1), lang="it")
            messages.extend(build_messages("system", f"Wikipedia dice: " + wikipedia_result))
        # engage ai and respond
        print("Engaging AI...")
        ai_response: str = ai.create_completion(messages)
        print("AI completion finished.")
        LAST_MESSAGES.extend(build_messages("assistant", ai_response))
        await message.reply(ai_response)
    except discord.Forbidden as e:
        print(f"Bot lacks permissions: {e}")
    except GPTAPIError as e:
        print(f"Chatgpt error: {e}")


if __name__ == "__main__":
    bot.run(BOT_TOKEN)