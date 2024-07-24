import os
import requests
import re
import logging
from dotenv import load_dotenv
from discord import Color, Embed, Intents, Client
from html import unescape
from flask_stuff import keep_alive

load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('TOKEN')

intents: Intents = Intents.default()
intents.message_content = True 
client: Client = Client(intents=intents)

ANILIST_API_URL = "https://graphql.anilist.co"

def search_anime(anime_name):
  query = '''
    query($search: String) {
      Media(search: $search, type: ANIME) {
        title {
          romaji
        }
        description
        coverImage {
          extraLarge
        }
        averageScore
      }
    }
  '''

  variables = {'search': anime_name}
  response = requests.post(ANILIST_API_URL, json={'query': query, 'variables': variables})
  if response.status_code == 200:
    return response.json()["data"]["Media"]
  else:
    return None
  
def clean_text(text):
  clean_text = unescape(text)
  clean_text = re.sub("<.*?>", "", clean_text)
  return clean_text


@client.event
async def on_ready():
  logging.info('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('$anime'):
    anime_name = message.content[len("$anime "):]
    anime_details = search_anime(anime_name)

    if anime_details:
      title = anime_details["title"]["romaji"]
      description = clean_text(anime_details["description"])[:200] + "..."
      image = anime_details["coverImage"]["extraLarge"]
      score = anime_details["averageScore"]

      embed = Embed(title=title, description=description, color=Color.red())
      embed.set_thumbnail(url=image)
      embed.set_image(url=image)
      embed.add_field(name="Score", value=score, inline=False)

      await message.channel.send(embed=embed)

    else:
      await message.channel.send("Anime not found")

keep_alive()
client.run(TOKEN)
