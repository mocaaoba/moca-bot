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

# To anybody reading this, this was the feature that won the poll. This was not by choice. Please don't judge.
# Although to any recruiters out there, the nhentai API is actually surprisingly not that well documented (in English) outside of a random Github user page. 
# You have no idea how much digging around this took.
def horny_on_main(query):
    dump = requests.get("https://nhentai.net/api/galleries/search?query=" + query + "&sort=popular")
    if dump is None:
        return "Moca-chan is a bit tired right now, how about you go look for your own degen stuff for once?", -1
    print(dump)
    jsonar = dump.json()
    result = jsonar["result"]
    num_nukes = len(result)
    if num_nukes == 0:
        return "Error 69: fetish not found", -1
    randomystery = random.randint(0, num_nukes - 1)
    id = result[randomystery]["id"]
    return "https://nhentai.net/g/" + str(id), result[randomystery]["media_id"]

# Fix spacing for wiki stuff
def fix_spacing(s):
    return s.replace(".", ". ").replace(".  ", ". ").replace(". )", ".)")
    
# Find a wiki page based on a search query (does not have to be exact)
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

def get_skill_info(url):
    html = requests.get(url).content
    parsed_html = BeautifulSoup(html, features="html.parser")
    for ttt in parsed_html.body.find_all('span', attrs={'class':'tooltiptext'}):
        ttt.decompose()
    for gw in parsed_html.body.find_all('sup', attrs={'class':'reference'}):
        gw.decompose()
    skills = parsed_html.body.find_all('td', attrs={'class':'skill-name'})
    descs =  parsed_html.body.find_all('td', attrs={'style':'text-align:left;'})
    if len(skills) == 0:
        return "Moca-chan didn't find anything there... are you sure you didn't make a typo?"
    response = ""
    for i in range(len(skills)):
        if i < len(descs):
            response += fix_spacing(skills[i].text) + ": "
            response += fix_spacing(descs[i].text) + "\n"
    return response

# Get host link for a quest
def get_host_link(url):
    html = requests.get(url).content
    parsed_html = BeautifulSoup(html, features="html.parser")
    return parsed_html.body.find('a', href=True, text='Start Quest')['href']

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
    
    # search the gbf wiki
    elif(message.content.startswith("search")):
        query = message.content[7:]
        wiki_url = wiki_search([query])
        await message.channel.send(wiki_url)
        
    elif(message.content.startswith("info")):
        query = message.content[5:]
        wiki_url = wiki_search([query])
        await message.channel.send(get_skill_info(wiki_url))
        
    elif(message.content.startswith("host")):
        query = message.content[5:]
        wiki_url = wiki_search([query])
        await message.channel.send(get_host_link(wiki_url))
        
    elif(message.content.startswith("gw")):
        query = message.content[3:]
        url = "http://gbf.gw.lt/gw-guild-searcher/search"
        r = requests.post(url, json={"search":query})
        json = r.json()
        msg = "http://game.granbluefantasy.jp/#guild/detail/" + str(json['result'][0]['id']) + "\n"
        data = json['result'][0]['data']
        for i in range(len(data)):
            msg += str(data[i]['name']) + " Ranked #" + str(data[i]['rank']) + " in GW #" + str(data[i]['gw_num']) + " with " + str(data[i]['points']) + " points\n"
        await message.channel.send(msg)
        
    # Check if this is the NSFW channel and there's a degen
    elif(message.channel.name == "nsfw" and message.content.startswith("degen")):
        query = message.content[6:]
        url, media_id = horny_on_main(query)
        if media_id == -1:
            await message.channel.send(url)
        else:
            e = discord.Embed(title=url)
            cover = "https://t.nhentai.net/galleries/" + str(media_id) + "/cover.jpg"
            e.set_image(url=cover)
            await message.channel.send(embed=e)
    
    # Check if this is the raids channel and there is exactly 1 picture attached
    elif (
            message.channel.name == "raids" or message.channel.name == "ubhl" or message.channel.name == "lucilius-hard" or message.channel.name == "gbf") and len(
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
