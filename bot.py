###########
## SETUP ##
###########
from PIL import Image, ImageChops, ImageEnhance
import os
import werkzeug
import ntpath
import datetime
import requests
import discord
import uuid
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "!", intents = intents)

@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if 'butter' in message.content.lower():
        print('buttered UP!')
        await message.channel.send('dog with da butta on it. butta dog.')
    await client.process_commands(message)

@client.command(pass_context=True)
async def printer(ctx, *, arg):
    print('printer running')
    await ctx.send(arg)

@client.command(pass_context=True)
async def b(ctx, *args):
    if len(ctx.message.attachments) > 0:
        png_file_name = ''
        for arg in args:
            png_file_name += arg + ' '
        if png_file_name.endswith(' '):
            png_file_name = png_file_name[:-1]
        png_file_name += uuid.uuid4().hex + '.png'
        png_file_name = png_file_name.lower()
        png_file_name = os.path.join('preJPGs/', png_file_name)
        await ctx.message.attachments[0].save(png_file_name)
        await ctx.message.channel.send('Getting buttered up...')
        try:
            image = Image.open(png_file_name)
        except Exception as err:
            #uh oh. Something went wrong.
            print('Uploaded image open error: ' + err)
            return 'Error: ' + err
        filename = process_image(image)
        attachmentName = ntpath.basename(filename)
        file = discord.File(filename, filename = attachmentName)
        embed = discord.Embed(title="Image With Da Butta On It", color=0x00ff00)
        embed.set_image(url= ("attachment://" + attachmentName))
        await ctx.message.channel.send(file=file, embed=embed)
        if os.path.exists(filename):
            os.remove(filename)
            os.remove(png_file_name)
    return


def process_image(img):
  #open up the mask
  mask = Image.open('mask.png')
  mask = mask.convert('RGBA')

  ratio = 614.0/984.0
  newHeight = round(ratio*img.width)
  newWidth = img.width
  if(newHeight > img.height):
    newHeight = img.height
    newWidth = round(newHeight*(1/ratio))
  mask = mask.resize((newWidth, newHeight))

  img.paste(mask, (round((img.width-newWidth)/2),0), mask)
  newdata = img.getdata()

  #create an image from our new combined data
  img.putdata(newdata)
  #unique name
  filename = uuid.uuid4().hex + '.png'
  filename = os.path.join('tmp/', filename)
  img.save(filename, 'PNG')
  #send it back
  return filename

client.run('Nzc5MjYxNTEwMDEzOTQzODI4.X7d91Q.7Ih9AckLi8mOpFzoh0nruTOc6D8')
