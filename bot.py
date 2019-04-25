import discord
from PIL import Image
import requests
from io import BytesIO
import os
import pytesseract

client = discord.Client()

@client.event
async def on_ready():
    print("The bot is ready!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.name == "raids" and len(message.attachments) == 1:
        attach = message.attachments[0]
        url = attach.url
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("LA")
        new_size = tuple(2*x for x in img.size)
        img = img.resize(new_size, Image.ANTIALIAS)
        black = (0, 0, 0)
        white = (255, 255, 255)
        threshold = (55, 55, 55)
        pixels = img.getdata()

        newPixels = []

        # Compare each pixel
        for pixel in pixels:
            if pixel < threshold:
                newPixels.append(black)
            else:
                newPixels.append(white)

        # Create and save new image.
        newImg = Image.new("RGB", img.size)
        newImg.putdata(newPixels)

        text = pytesseract.image_to_string(newImg).replace("S", "8").replace("O", "0").replace("Z", "2")
        print(text)
        start = text.find("ID") + 4
        if start == 3:
            await message.channel.send("Oops, I can't quite see the raid code. I have trouble reading it if there's cut-off text above it.")
        else:
            text = text[start: start + 8]
            await message.channel.send(text)

client.run(os.environ['TOKEN'])
