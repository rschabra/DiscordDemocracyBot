###########
## SETUP ##
###########
import os
import werkzeug
import ntpath
from time import time, sleep
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import math
from datetime import datetime, timedelta
import sched
import requests
import discord
import uuid
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True

global in_action
in_action = False
global usertomute
global num_thumbs
num_thumbs = 0

global s
s = BackgroundScheduler()
global asyncs
asyncs = AsyncIOScheduler()

client = commands.Bot(command_prefix = "!", intents = intents)



@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('Hey there! I\'m DemocracyBot. I\'m not here just to be used to mute Carlos, though! My goal is to bring Democracy to Discord. \nSome ground rules: Don\'t Abuse It. ')
        break

@client.command(pass_context=True)
async def rules(ctx):
    await ctx.send('**Rules:** \n\t1. The requestor and requestee have to be in a voice channel.\n\t2. The requestor and requestee must be in the same voice channel.\n\t3. The number of votes required is 3/4 of the people in the voice channel.')

@client.command(pass_context=True)
async def mute(ctx, *, args):
    global num_thumbs
    global in_action
    global usertomute
    global s

    msg = ctx.message
    requestor = msg.author
    guild = client.get_guild(msg.guild.id)
    member = guild.get_member(msg.mentions[0].id)
    check_requestor = await check_req(requestor, member)
    if in_action == False and check_requestor == True:
        num_to_get = await check_num(member)
        new_msg = await ctx.send('Vote - {} would like to mute {} for 10 mins. Please react with :thumbsup: for a Yes vote. If there are {} Yes votes in the next one minute, {} will be muted.'.format(ctx.author, args, num_to_get, args),
        delete_after=60)
        await new_msg.add_reaction('👍')
        await new_msg.add_reaction('👎')
        dd = datetime.now() + timedelta(seconds=60)
        in_action = True
        usertomute = args
        s.remove_all_jobs()
        s.add_job(reset, 'date', run_date=dd)
        s.start()
    elif in_action == False and check_requestor == False:
        await ctx.send('Both the requestor and the requestee have to be in the same channel.', delete_after=20)
    else:
        await ctx.send('You cannot call two votes at the same time. Please try again once the previous vote ends.', delete_after=20)

def reset():
    global in_action
    global num_thumbs
    num_thumbs = 0
    in_action = False
    x = False


@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == client.user:
        if reaction.emoji == '👍':
            if reaction.message.content[0:4] == 'Vote':
                global num_thumbs
                num_thumbs += 1
                print(num_thumbs)
                await reaction_count_check(reaction.message)
        if reaction.emoji == '👎':
            if reaction.message.content[0:4] == 'Vote':
                num_thumbs -= 1
                print(num_thumbs)
                await reaction_count_check(reaction.message)

@client.event
async def on_reaction_remove(reaction, user):
    if reaction.message.author == client.user:
        if reaction.emoji == '👍':
            if reaction.message.content[0:4] == 'Vote':
                global num_thumbs
                num_thumbs -= 1
                print(num_thumbs)

async def reaction_count_check(msg):
    global usertomute
    global num_thumbs
    global in_action
    global s
    guild = client.get_guild(msg.guild.id)
    member = guild.get_member(msg.mentions[0].id)
    num_to_get = await check_num(member)
    if num_thumbs >= num_to_get:
        num_thumbs = 0
        in_action = False
        await member.edit(mute = True)
        await msg.channel.send("{} has been muted".format(usertomute), delete_after=30)
        s.remove_all_jobs()
        dd = datetime.now() + timedelta(minutes = 10)
        kwags = {'arg2': member, 'arg1': msg}
        asyncs.add_job(unmute_mem, 'date', run_date=dd, kwargs = kwags)
        asyncs.start()

async def unmute_mem(**kwags):
    global usertomute
    await kwags['arg2'].edit(mute = False)
    await kwags['arg1'].channel.send("{} has been unmuted after 10 mins".format(usertomute), delete_after = 20)
    asyncs.remove_all_jobs()

async def check_num(member):
    con_chan = member.voice.channel
    chan_mems_length = len(con_chan.members)
    print(chan_mems_length)
    return math.ceil((chan_mems_length*3)/4)

async def check_req(req, mem):
    try: 
        req_chan = req.voice.channel
    except:
        return False
    try:
        mem_chan = mem.voice.channel
    except:
        False
    if req_chan == mem_chan:
        return True
    else:
        return False

client.run('ODY1ODI5NzIyNzEzMjI3MjY0.YPJsxA.yCVjXLGmNM4lri8UIjWmVpqXkQE')
