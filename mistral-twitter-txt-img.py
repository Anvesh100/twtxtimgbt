import tweepy
from PIL import Image, ImageDraw, ImageFont
import requests
import time
from io import BytesIO

# Twitter API credentials
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
access_token = "YOUR_ACCESS_TOKEN"
access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Function to create circular profile image
def create_circular_profile_image(profile_pic_url):
    response = requests.get(profile_pic_url)
    profile_pic = Image.open(BytesIO(response.content))
    diameter = min(profile_pic.size)
    mask = Image.new("L", profile_pic.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter, diameter), fill=255)
    masked_profile_pic = ImageOps.fit(profile_pic, mask.size)
    masked_profile_pic.putalpha(mask)
    return masked_profile_pic

# Function to create image with circular profile picture, name, username, and tweet text
def create_image_with_profile_pic(profile_pic_url, name, username, tweet_text):
    profile_pic = create_circular_profile_image(profile_pic_url)
    img = Image.new('RGB', (500, 600), color=(255, 255, 255))
    img.paste(profile_pic, (10, 10))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text((150, 10), f"Name: {name}", font=font, fill=(0, 0, 0))
    draw.text((150, 40), f"Username: @{username}", font=font, fill=(0, 0, 0))
    draw.text((10, 150), "Tweet Text:", font=font, fill=(0, 0, 0))
    draw.text((10, 180), tweet_text, font=font, fill=(0, 0, 0))
    return img

# Function to handle mentions
def handle_mentions():
    try:
        mentions = api.mentions_timeline()
        for mention in mentions:
            tweet_id = mention.id
            username = mention.user.screen_name
            name = mention.user.name
            tweet_text = mention.text.replace(f"@{username}", "").strip()
            profile_pic_url = mention.user.profile_image_url

            # Create image with profile pic, name, username, and tweet text
            tweet_image = create_image_with_profile_pic(profile_pic_url, name, username, tweet_text)

            # Save combined image
            tweet_image.save(f"{username}_tweet_image.jpg")

            # Reply to the mention with the image
            api.update_with_media(f"{username}_tweet_image.jpg", status=f"@{username} Here's your tweet in image form!")

            # Delete the mention tweet
            api.destroy_status(tweet_id)

            # Add a delay between API calls to avoid rate limits
            time.sleep(15)  # Delay for 15 seconds

    except tweepy.TweepError as e:
        print(f"An error occurred: {str(e)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the bot
while True:
    handle_mentions()
