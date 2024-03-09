import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont
import tweepy
from airtable import Airtable
import time

# Replace the following lines with your own API keys and Airtable API key
API_KEY = 'your_api_key'
API_SECRET_KEY = 'your_api_secret_key'
ACCESS_TOKEN = 'your_access_token'
ACCESS_TOKEN_SECRET = 'your_access_token_secret'
AIRTABLE_API_KEY = 'your_airtable_api_key'

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
airtable = Airtable("Your Airtable Base", "Your Table Name", AIRTABLE_API_KEY)

class TwitterBot:
    def reply_with_image_and_text(self, status):
        try:
            text = status.text
            username = status.user.screen_name
            profile_image_url = status.user.profile_image_url

            # Add text and username to Airtable
            airtable.insert({'Name': username, 'Text': text}, typecast=True)

            # Convert text into an image
            img = Image.new('RGB', (300, 40), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), text, font=ImageFont.truetype('arial.ttf', 16), fill=(0, 0, 0))

            # Load user's profile picture
            user_profile_image = io.BytesIO(requests.get(profile_image_url).content)
            user_profile_image = Image.open(user_profile_image)
            user_profile_image.thumbnail((80, 80), Image.ANTIALIAS)

            # Merge user profile picture and text
            img = Image.alpha_composite(img, profile_image.convert('RGBA'))

            # Save the image
            response = io.BytesIO()
            img.save(response, format='JPEG')
            response.seek(0)

            # Upload the image to Twitter
            media = api.media_upload(filename='image.jpg', file=response)

            # Reply        # Reply to the tweet
            api.update_status(status=f'Here is your text as an image:\n\n{text}', in_reply_to_status_id=status.id, media_ids=[media.media_id])

        except Exception as e:
            print(f'Error: {str(e)}')

if __name__ == '__main__':
    bot = TwitterBot()
    while True:
        try:
            mentions = api.mentions_timeline()
            for mention in mentions:
                bot.reply_with_image_and_text(mention)
            time.sleep(10)
        except Exception as e:
            print(f'Error: {str(e)}')