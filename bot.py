import discord
from PIL import Image
import requests
from io import BytesIO
import os
import pytesseract
import base64
import io

#Some boilerplate discord bot stuff
client = discord.Client()

@client.event
async def on_ready():
    print("The bot is ready!")

@client.event
async def on_message(message):
    #Don't reply to your own messages
    if message.author == client.user:
        return
    
    #Check if this is the raids channel and there is exactly 1 picture attached
    if (message.channel.name == "raids" or message.channel.name == "ubhl" or message.channel.name == "lucilius-hard") and len(message.attachments) == 1:
        attach = message.attachments[0]
        
        #Url of the attachment
        url = attach.url
        
        #Get information from the url
        response = requests.get(url)
        
        #Open the image from the url and convert to grayscale
        img = Image.open(BytesIO(response.content)).convert("LA")
        
        #Double image size for better reading
        new_size = tuple(2*x for x in img.size)
        img = img.resize(new_size, Image.ANTIALIAS)
        
        #Convert image to black and white
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

        # Create new image to read
        newImg = Image.new("RGB", img.size)
        newImg.putdata(newPixels)

        #Path to tesseract binary or something
        pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
        
        #Feed image into black box to read it. Replace letters that can't be in a Raid ID with what they probably are
        text = pytesseract.image_to_string(newImg).replace("S", "8").replace("O", "0").replace("Z", "2")
        
        #Debugging this piece of pasta
        print(text)
        
        #The start of the raid code
        start = text.find("ID") + 4
        
        #Only send the code if we actually found the Raid ID. Otherwise the image is either not a raid code or we couldnt read it.
        if start != 3:
            text = text[start: start + 8]
            text = text.replace("I", "1")
            if text.find(" ") != -1:
                await message.channel.send("Sorry this feature requires 5 buns to unlock. To get more buns, please change your resolution to standard")
            else:
                await message.channel.send(text)
            if message.content == "debug":
                with io.BytesIO() as output:
                    newImg.save(output, format="PNG")
                    contents = output.getvalue()
                    strings = []
                    while len(contents) > 2000:
                        strings.append(contents[0: 2000])
                        contents = contents[2000:]
                    for s in strings:
                        await message.channel.send(s)

#Stuff for hosting it
client.run(os.environ['TOKEN'])
