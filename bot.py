import asyncio
import datetime
import requests
import discord
import html2text


def readHeader(header):
    with open('env.txt', 'r') as f:
        for line in f.readlines():
            if header in line:
                return line.replace(f'{header}=', '').replace(' ', '')


channel_id = int(readHeader('CHANNEL_ID'))
WHEN = datetime.time(12, 0, 0)
wishlist_url = readHeader('WISHLIST_URL')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')


async def daily_msg():
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    await channel.send(f'@everyone\nAktueller Preis **{read_html()}€**' +
                       f'\n*Am: [{datetime.datetime.today().strftime("%d:%M:%Y")}]*')


async def halt_Task(now):
    tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
    seconds = (tomorrow - now).total_seconds()
    await asyncio.sleep(seconds)


async def timer_task():
    now = datetime.datetime.now()
    if now.time() > WHEN:
        await halt_Task(now)
    while True:
        now = datetime.datetime.now()
        target_time = datetime.datetime.combine(now.date(), WHEN)
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
    TOKEN = readHeader('DISCORD_TOKEN')
    client.loop.create_task(timer_task())
    client.run(TOKEN)
