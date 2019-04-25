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
        black = (0, 0, 0)
        white = (255, 255, 255)
        threshold = (50, 50, 50)
        pixels = img.getdata()

        newPixels = []

        # Compare each pixel
        for pixel in pixels:
            if pixel < threshold:
                newPixels.append(white)
            else:
                newPixels.append(black)

        # Create and save new image.
        newImg = Image.new("RGB", img.size)
        newImg.putdata(newPixels)

        text = pytesseract.image_to_string(newImg)
        print(text)
        start = text.find("ID: ") + 4
        if start == 3:
            await message.channel.send("Oops, I can't quite see the raid code. Looks like you'll have to type it out manually.")
        else:
            text = text[start: start + 8]
            await message.channel.send(text)

client.run(os.environ['TOKEN'])
