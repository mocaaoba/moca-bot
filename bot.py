import discord
from PIL import Image
import requests
from io import BytesIO
import os
import pytesseract
import base64
import io

# Some boilerplate discord bot stuff
client = discord.Client()


@client.event
async def on_ready():
    print("The bot is ready!")


@client.event
async def on_message(message):
    # Don't reply to your own messages
    if message.author == client.user:
        return

    if (message.content.startswith("!r")):
        sindex = message.content.rfind(':')
        eindex = message.content.rfind('>')
        id = message.content[sindex + 1:eindex]
        url = "https://cdn.discordapp.com/emojis/" + id + ".png?v=1"
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        newImg = img.transpose(Image.FLIP_LEFT_RIGHT)
        #newImg = newImg.resize((32,32), Image.ANTIALIAS)
        newImg.thumbnail((32, 32), Image.ANTIALIAS)
        buf = io.BytesIO()
        newImg.save(buf, 'png', quality=100)
        buf.seek(0)
        await message.channel.send(file=discord.File(buf, 'reversed.png'))
        
    if (message.content.startswith("!f")):
        if (len(message.attachments) != 1):
            await message.channel.send("Moca-chan is a genius, but she can't do anything if you don't attach exactly one file.")
        else:
            attach = message.attachments[0]
            url = attach.url
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            newImg = img.transpose(Image.FLIP_LEFT_RIGHT)
            #newImg = newImg.resize((32,32), Image.ANTIALIAS)
            buf = io.BytesIO()
            newImg.save(buf, 'png')
            buf.seek(0)
            await message.channel.send(file=discord.File(buf, 'reversed.png'))

    # Check if this is the raids channel and there is exactly 1 picture attached
    if (
            message.channel.name == "raids" or message.channel.name == "ubhl" or message.channel.name == "lucilius-hard") and len(
            message.attachments) == 1:
        attach = message.attachments[0]

        # Url of the attachment
        url = attach.url

        # Get information from the url
        response = requests.get(url)

        # Open the image from the url and convert to grayscale
        img = Image.open(BytesIO(response.content)).convert("LA")

        # Double image size for better reading
        #new_size = tuple(2 * x for x in img.size)
        #img = img.resize(new_size, Image.ANTIALIAS)

        # Convert image to black and white
        black = (0, 0, 0)
        white = (255, 255, 255)
        threshold = (55, 55, 55)
        pixels = img.getdata()
        newPixels = [None] * (4 * len(pixels))
        n, m = img.size
        for x in range(len(pixels)):
            color = white
            if pixels[x] < threshold:
                color = black
            newPixels[2 * int(x / n) * 2 * n + 2 * (x % n)] = color
            newPixels[2 * int(x / n) * 2 * n + 2 * (x % n) + 1] = color
            newPixels[(2 * int(x / n) + 1) * 2 * n + 2 * (x % n)] = color
            newPixels[(2 * int(x / n) + 1) * 2 * n + 2 * (x % n) + 1] = color
                
        #finalpix = [None] * (4 * len(newPixels))
        #n, m = img.size
        #for x in range(len(newPixels)):
        #    finalpix[2 * int(x / n) * 2 * n + 2 * (x % n)] = newPixels[x]
        #    finalpix[2 * int(x / n) * 2 * n + 2 * (x % n) + 1] = newPixels[x]
        #    finalpix[(2 * int(x / n) + 1) * 2 * n + 2 * (x % n)] = newPixels[x]
        #    finalpix[(2 * int(x / n) + 1) * 2 * n + 2 * (x % n) + 1] = newPixels[x]

        # Create new image to read
        new_size = tuple(2 * x for x in img.size)
        newImg = Image.new("RGB", new_size)
        newImg.putdata(newPixels)
        #new_size = tuple(2 * x for x in img.size)
        #newImg = Image.new("RGB", new_size)
        #newImg.putdata(finalpix)
        
        
        
        new_size = tuple(2 * x for x in newImg.size)
        newImg = newImg.resize(new_size, Image.ANTIALIAS)

        # Path to tesseract binary or something
        pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'

        # Feed image into black box to read it. Replace letters that can't be in a Raid ID with what they probably are
        text = pytesseract.image_to_string(newImg).replace("S", "8").replace("O", "0").replace("Z", "2").replace("Q", "0")
        saveText = text

        # Debugging this piece of pasta
        print(text)

        # The start of the raid code
        start = text.find("ID") + 4
        
        if message.content == "debug":
                byteImgIO = io.BytesIO()
                newImg.save(byteImgIO, "PNG")
                byteImgIO.seek(0)
                await message.channel.send(saveText)
                await message.channel.send(file=discord.File(byteImgIO, 'debug.png'))
                #new_size = tuple(2 * x for x in newImg.size)
                #bigImg = newImg.resize(new_size, Image.ANTIALIAS)

        # Only send the code if we actually found the Raid ID. Otherwise the image is either not a raid code or we couldnt read it.
        if start != 3:
            text = text[start: start + 8]
            text = text.replace("I", "1")
            if text.find(" ") != -1:
                await message.channel.send(
                    "Sorry this feature requires 5 buns to unlock. To get more buns, please change your resolution to standard")
            else:
                await message.channel.send(text)


# Stuff for hosting it
client.run(os.environ['TOKEN'])
