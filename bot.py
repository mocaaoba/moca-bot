import discord
from PIL import Image
from PIL import ImageFilter
import requests
from io import BytesIO
import os
import pytesseract
import base64
import io
import time
import requests
import random
from bs4 import BeautifulSoup
from googlesearch import search

prefix = "https://gbf.wiki"
separator = "/"

# Some boilerplate discord bot stuff
client = discord.Client()

def horny_on_main(query):
    dump = requests.get("https://nhentai.net/api/galleries/search?query=" + query)
    jsonar = dump.json()
    result = jsonar["result"]
    num_nukes = len(result)
    if num_nukes == 0:
        return "Error 69: fetish not found"
    randomystery = random.randint(0, num_nukes - 1)
    id = result[randomystery]["id"]
    return "https://nhentai.net/g/" + str(id)
    

def wiki_search(query):
    prefixed_query = [prefix] + query
    wiki_url = separator.join(prefixed_query)

    html = requests.get(wiki_url).content
    soup = BeautifulSoup(html, 'html.parser')

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())

    chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
    text = " ".join(chunk for chunk in chunks if chunk)

    #print(text)

    #URL does not exist on wiki
    #TODO: Add condition to deal with redirects
    if text.find("There is currently no text in this page.") != -1:
        for result in search(" ".join(["gbf wiki"] + query), tld='com', lang='en', num=1, start=0, stop=1, pause=2.0):
            wiki_url = result
            end_index = wiki_url.find("?")
            if end_index != -1:
                wiki_url = wiki_url[:end_index]

    return wiki_url

@client.event
async def on_ready():
    print("The bot is ready!")

@client.event
async def on_message(message):
    # Don't reply to your own messages
    if message.author == client.user:
        return

    if (message.content.find("571004166604849162") != -1):
        await message.channel.send("Could you please stop overworking Moca-chan? Maybe Moca-chan should just go back to sleep...")
    
    elif (message.content.startswith("!r")):
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
        
    elif (message.content.startswith("!f")):
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

    elif (message.content.startswith("dev")):
        attach = message.attachments[0]

        # Url of the attachment
        url = attach.url

        start = time.time()
        
        # Get information from the url
        response = requests.get(url)

        # Open the image from the url and convert to grayscale
        img = Image.open(BytesIO(response.content))
        
        img.filter(ImageFilter.SMOOTH)
        threshold = 125
        black = (0, 0, 0)
        white = (255, 255, 255)
        test = True
        newimg = img
        if not test:
            pixels = img.getdata(band=1)
            newpixels = []
            for pixel in pixels:
                if pixel < threshold:
                    newpixels.append(black)
                else:
                    newpixels.append(white)
                
            newimg = Image.new("RGB", img.size)
            newimg.putdata(newpixels)
        
        new_size = tuple(2 * x for x in newimg.size)
        newimg = newimg.resize(new_size, Image.ANTIALIAS)
        
        preprocess = time.time() - start
        
        pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
        
        start = time.time()
        text = pytesseract.image_to_string(newimg, config='-psm 7').replace("S", "8").replace("O", "0").replace("Z", "2").replace("Q", "0").replace("L", "1").replace("G", "6")
        saveText = text
        ocr = time.time() - start
        
        # The start of the raid code
        start = text.find("ID") + 4
        if start == 3:
            start = text.find("1D") + 4
            
        await message.channel.send(saveText)
        await message.channel.send("preprocess: " + str(preprocess) + " ocr: " + str(ocr))
        if start != 3:
            text = text[start: start + 8]
            text = text.replace("I", "1")
            if text.find(" ") != -1:
                await message.channel.send(
                    "Sorry this feature requires 5 buns to unlock. To get more buns, please change your resolution to standard")
            else:
                await message.channel.send(text)
    
    # Check if this is the bot-related channel
    elif(message.channel.name == "bot-related" and message.content.startswith("search")):
        query = message.content[7:]
        wiki_url = wiki_search([query])
        await message.channel.send(wiki_url)
        
    # Check if this is the NSFW channel and there's a degen
    elif(message.channel.name == "nsfw" and message.content.startswith("degen")):
        query = message.content[6:]
        url = horny_on_main(query)
        await message.channel.send(url)
    
    # Check if this is the raids channel and there is exactly 1 picture attached
    elif (
            message.channel.name == "raids" or message.channel.name == "ubhl" or message.channel.name == "lucilius-hard") and len(
            message.attachments) == 1:
        attach = message.attachments[0]

        # Url of the attachment
        url = attach.url

        # Get information from the url
        response = requests.get(url)

        # Open the image from the url and convert to grayscale
        img = Image.open(BytesIO(response.content))
        
        img.filter(ImageFilter.SHARPEN)
        threshold = 125
        black = (0, 0, 0)
        white = (255, 255, 255)
        #pixels = img.getdata(band=1)
        #newpixels = []
        #for pixel in pixels:
            #if pixel < threshold:
                #newpixels.append(black)
            #else:
                #newpixels.append(white)
                
        #newimg = Image.new("RGB", img.size)
        #newimg.putdata(newpixels)
        newimg = img
        
        new_size = tuple(2 * x for x in newimg.size)
        newimg = newimg.resize(new_size, Image.ANTIALIAS)
        
        pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
        
        text = pytesseract.image_to_string(newimg, config='-psm 7').replace("S", "8").replace("O", "0").replace("Z", "2").replace("Q", "0").replace("L", "1").replace("G", "6")
        saveText = text
        
        # The start of the raid code
        start = text.find("ID") + 4
        if start == 3:
            start = text.find("1D") + 4

        if start != 3:
            text = text[start: start + 8]
            text = text.replace("I", "1")
            if text.find(" ") != -1:
                await message.channel.send(
                    "Sorry, Moca-chan had some trouble reading that last image. Have you considered buying Moca-chan some buns?")
            else:
                await message.channel.send(text)


# Stuff for hosting it
client.run(os.environ['TOKEN'])
