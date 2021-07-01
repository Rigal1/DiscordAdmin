# -*- coding: utf-8 -*-
"""
Created on Wed May 12 09:41:59 2021

@author: iriut
"""

from discord.ext import commands
import os
import discord
import re

WELCOME_ID = 841966135925669889
QUEST_ID = 841829762094858290

RIGAL_ID = 632853740159762435
MEMBER_ID = 841736942332805150
ZATSUDAN_ID = 841733816061526126

ROLE_1 = 842979563188912129
ROLE_2 = 842979856182018088
ROLE_3 = 842979862326542386

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents = intents)
#token = os.environ['DISCORD_BOT_TOKEN']
#token = "ODE0NDE1NjIzMTgxMzAzODE4.YDdhpw.RlwZuykhj5jfI0krIljRACeTFgg"  #テスト用bot
token = "ODQxODQwNDYxNTA5NDI3MjMx.YJsnBg.V3bLNxnIJx_umtOYh0ZiwOYbIKI" #本番環境
#embed_sample = discord.Embed(title = "タイトル", description = "内容", url = "https://www.google.co.jp/")


async def get_message(ctx, message_id):
    guild = ctx.guild
    channel = guild.get_channel(QUEST_ID)
    message = await channel.fetch_message(message_id)
    return message

@bot.event
async def on_ready():
    print("Log in")
    
async def add_role_command(payload):
    guild = bot.get_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)
    role = guild.get_role(MEMBER_ID)
    await member.add_roles(role)
    channel = guild.get_channel(ZATSUDAN_ID)
    await channel.send(f'{member.mention} ようこそ！')
    
async def remove_role_command(payload):
    guild = bot.get_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)
    role = guild.get_role(MEMBER_ID)
    await member.remove_roles(role)
    
async def add_message_embed(text, guild):
    #embed = embed_sample.copy()
    embed = discord.Embed(title = text[1], description = text[2], url = text[3])
    channel = guild.get_channel(text[0])
    await channel.send(embed=embed)
    
async def call_rigal(text = "見てる？"):
    rigal = await bot.fetch_user(RIGAL_ID)
    await rigal.send(text)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return
    #print(payload.channel_id)
    if payload.message_id == WELCOME_ID:
        await add_role_command(payload)
    elif payload.channel_id == QUEST_ID:
        guild = bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = await guild.fetch_member(payload.user_id)
        title = message.embeds[0].title
        text = f"{member}　が「{title}」にリアクションしました！"
        await call_rigal(text)
    
@bot.event
async def on_raw_reaction_remove(payload):
    
    if payload.message_id == WELCOME_ID:
        await remove_role_command(payload)
    
    """
@bot.event
async def on_message(message):
    await message.add_reaction("✅")
"""
@bot.command()
async def temp(ctx):
    await ctx.send("T:\nD:\nL:\nC:")

async def markdown(text):
    result = [0, "", "", ""]
    channel = re.findall(r"C:(.*)", text)
    title = re.findall(r"T:(.*)\nD:", text)
    description = re.findall(r"D:(.+?)\nL:", text, flags = re.DOTALL)
    url = re.findall(r"L:(.*)\nC:", text)
    result[0] = int(channel[0])
    result[1] = title[0]
    result[2] = description[0]
    if url:
        result[3] = url[0]
    return result

@bot.command()
async def contact(ctx, *, arg):
    text = await markdown(arg)
    await add_message_embed(text, ctx.guild)

@bot.command()
async def addQ(ctx, arg1, arg2, arg3, arg4, arg5, arg6 = 0):
    text = f"人数：{arg2}　リミット：{arg3}　\n舞台：{arg4}　タイプ：{arg5}"
    color = 0xffeb3b
    if arg6:
        color = 0x3f51b5
    embed = discord.Embed(title = arg1, description = text, color = color)
    channel = ctx.guild.get_channel(841829762094858290)
    await channel.send(embed = embed)

@bot.command()
async def clearLog(ctx, arg):
    if ctx.author.guild_permissions.administrator and arg == "-all":
        if arg == "-all":            
            await ctx.channel.purge()
        else:
            await ctx.send("-allを付けてください")

async def get_quest_message(guild, title):
    channel = guild.get_channel(QUEST_ID)
    

async def start_quest(ctx, member_id, title_num, title):
    guild = ctx.guild
    role_id = await role_check(title_num)
    role = guild.get_role(role_id)
    await role.edit(name = title_num + title)
    await add_quest_role(guild, member_id, role)

async def role_check(title_num):
    role_id = 0
    if title_num == "【1】":
        role_id = ROLE_1
    elif title_num == "【2】":
        role_id = ROLE_2
    elif title_num == "【3】":
        role_id = ROLE_3
        
    return role_id

async def add_quest_role(guild, member_id, role):
    for ID in member_id:
        member = await guild.fetch_member(int(ID))
        await member.add_roles(role)
        
    

async def split_text(ctx, text):
    channel = ctx.channel
    member = re.findall(r"<@!(.+?)>", text)
    title = re.findall(r"「(.*)」", text)
    title_num = channel.name
    await start_quest(ctx, member, title_num, title[0])
    await channel.edit(name = title_num + title[0])

@bot.command()
async def start(ctx, *, arg):
    if ctx.author.guild_permissions.administrator:
        await split_text(ctx, arg) 

@bot.command()
async def end(ctx):
    if ctx.author.guild_permissions.administrator:
        channel_name = ctx.channel.name
        role_id = await role_check(channel_name[0:3])
        guild = ctx.guild
        role = guild.get_role(role_id)
        members = role.members
        for member in members:
            await member.remove_roles(role)
        await ctx.channel.edit(name = channel_name[0:3])
        await role.edit(name = channel_name[0:3])
        await ctx.send("-------------------------")
    
    
@bot.command()
async def emd_test(ctx):
    message = await get_message(ctx, 842820691002130493)
    embed = discord.Embed(title = "titleだぞっ☆")
    await message.edit(embed = embed)

@bot.command()
async def change(ctx, arg1, arg2, arg3, arg4, arg5, arg6 = 0, arg7 = 0):
    text = f"人数：{arg2}　リミット：{arg3}　\n舞台：{arg4}　タイプ：{arg5}"
    color = 0xffeb3b
    if arg6:
        color = 0x3f51b5
    embed = discord.Embed(title = arg1, description = text, color = color)
    channel = ctx.guild.get_channel(841829762094858290)
    message = await get_message(ctx, arg7)
    await message.edit(embed = embed)



bot.run(token)


"""        

@bot.command()
async def house(ctx, arg):
    text = arg
    embed = discord.Embed(title = "シノビガミハウスルール", description = text, color = 0x00bcd4, url = "https://drive.google.com/file/d/1rm6-8JvVfXfdARV9ImQTENdewEnRivD-/view?usp=sharing")
    channel = ctx.guild.get_channel(841742602126753812)
    await channel.send(embed = embed)

@bot.command()
async def react(ctx):
    react_id = 841966135925669889
    channel = ctx.guild.get_channel(841734326553935904)
    message = await channel.fetch_message(react_id)
    await message.add_reaction("✅")


    
@bot.command()
async def com1(ctx):
    embed = discord.Embed(title = "初回起動設定")
    embed.add_field(name = "操作説明", value = "この鯖の説明です", inline = False)
    embed.add_field(name = "ゲーム説明", value = "リガルGMのハウスルールです", inline = False)
    channel = ctx.guild.get_channel(841734347563597824)
    await channel.send(embed = embed)
    
@bot.command()
async def com2(ctx):
    embed = discord.Embed(title = "ホーム画面")
    embed.add_field(name = "掲示板", value = "こちらからのお知らせを掲載します", inline = False)
    embed.add_field(name = "クエスト一覧", value = "現在回せるシナリオ一覧です", inline = False)
    embed.add_field(name = "クエスト受付", value = "やりたいシナリオがある場合、ここに何らかのリアクションを付けてください", inline = False)
    embed.add_field(name = "神社", value = "ダイスbotを振るところです。基本的にダイスbotはここで振ってください。先頭に/rを付けるとダイスを振ることができます", inline = False)
    embed.add_field(name = "開発要望", value = "「これをしてほしい！」というものがありましたらこちらへお願いします", inline = False)
    channel = ctx.guild.get_channel(841734347563597824)
    await channel.send(embed = embed)
    
@bot.command()
async def com3(ctx):
    embed = discord.Embed(title = "進行中クエスト", description = "現在進行している卓です")
    channel = ctx.guild.get_channel(841734347563597824)
    await channel.send(embed = embed)
    
@bot.command()
async def com4(ctx):
    embed = discord.Embed(title = "出撃", description = "セッションのVCなどはここを使用します")
    embed.add_field(name = "クエスト通達事項", value = "聞き専用です", inline = False)
    channel = ctx.guild.get_channel(841734347563597824)
    await channel.send(embed = embed)

@bot.command()
async def com5(ctx):
    embed = discord.Embed(title = "クエスト履歴", description = "シナリオ毎にシナリオシートを掲載しています。\n単発は一幕シナリオ、長編は二幕以上のシナリオとなっています")
    channel = ctx.guild.get_channel(841734347563597824)
    await channel.send(embed = embed)    

"""