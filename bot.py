import os, asyncio
from datetime import datetime, timedelta, time
import requests
from dotenv import load_dotenv
import discord, html2text

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
channel_id = int(os.getenv('CHANNEL_ID'))
WHEN = time(12, 0, 0)
wishlist_url = os.getenv('WISHLIST_URL')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')


async def daily_msg():
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    await channel.send(f'@everyone\nAktueller Preis **{read_html()}€**\n*Am: [{datetime.today().strftime("%d:%M:%Y")}]*')


async def halt_Task(now):
    tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
    seconds = (tomorrow - now).total_seconds()
    await asyncio.sleep(seconds)


async def timer_task():
    now = datetime.now()
    if now.time() > WHEN:
        await halt_Task(now)
    while True:
        now = datetime.now()
        target_time = datetime.combine(now.date(), WHEN)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)
        await daily_msg()
        await halt_Task(now)


def read_html():
    params = {'': '', 'render': 'download'}
    html = requests.get(wishlist_url, params=params).text
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(html).strip().splitlines()
    c = 0
    for line in text:
        c += 1
        if line.find('Gesamtpreis') >= 0:
            return text[c+1].replace('€ ', '')


if __name__ == '__main__':
    client.loop.create_task(timer_task())
    client.run(TOKEN)
