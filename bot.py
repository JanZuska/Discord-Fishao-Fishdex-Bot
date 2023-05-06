#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
__author__ = "Jan Zuska"
__date__ = "2023/4/24"
__copyright__ = "Copyright 2023, Jan Zuska"
__credits__ = []
__license__ = "GPLv3"
__version__ = "1.3.3"
__maintainer__ = "Jan Zuska"
__email__ = "jan.zuska.04@gmail.com"
__status__ = "Production"
# ----------------------------------------------------------------------------
import discord
import json
from discord.ext import commands
import datetime
from PIL import Image
import os
import random

with open("fishao-data.json", "r") as file:
    data: list = json.load(file)
    file.close()

with open("config.json", "r") as file:
    config = json.load(file)
    API_KEY: str = config["API_KEY"]
    file.close()

with open("emoji.json", "r") as file:
    emoji: dict = json.load(file)
    file.close()

with open("location.json", "r") as file:
    locations: dict = json.load(file)
    file.close()

class Get():
    @staticmethod
    def Emoji(emoji_name: str, directory: str = "baits") -> str:
        for name, value in emoji[directory].items():
            if name == emoji_name:
                return value

    @staticmethod
    def LocationName(location_id: int) -> str:
        for id, details in locations.items():
            if int(id) == int(location_id):
                return details["name"]
            
    @staticmethod        
    def LocationId(location: str) -> int:
        for id, details in locations.items():
            for key, value in details.items():
                if value != location:
                    break
                return int(id)
            
    @staticmethod        
    def BadgeId(location: str) -> str:
        for id, details in locations.items():
            for key, value in details.items():
                if value != location:
                    break
                return details["badge_id"]

    @staticmethod
    def LocationsList():
        locations_list = []
        for id, deatils in locations.items():
            locations_list.append(deatils["name"])
        return locations_list

# ---------------------------------------------------------------

def TodayIsInInterval(interval: str) -> bool:
    today = datetime.date.today()
    year_now = today.year
    interval_start = interval.split("-")[0]
    interval_end = interval.split("-")[1]
    start_date = datetime.date(year_now, int(interval_start.split(".")[0]), int(interval_start.split(".")[1]))
    enf_date = datetime.date(year_now, int(interval_end.split(".")[0]), int(interval_end.split(".")[1]))
    if start_date <= today <= enf_date:
        return True
    else: 
        return False

def split_list(input_list: list, max_list_size: int = 25) -> list:
        output_list = []
        for i in range(0, len(input_list), max_list_size):
            output_list.append(input_list[i:i + max_list_size])
        return output_list

def FormatDate(date):
    dates = date.split("-")
    dates = [i.split(".") for i in dates]
    today = datetime.date.today()
    formated_date = []
    for d in dates:
        temp_date = datetime.date(year = today.year, month = int(d[0]), day = int(d[1]))
        temp_date = temp_date.strftime("%d.%m")
        formated_date.append(temp_date)
    return f"{formated_date[0]} - {formated_date[1]}"

async def FileCoding():
    now = datetime.datetime.now()
    current_time = now.strftime("%M%S%f")
    random_number = random.randint(100000, 1000000)
    return f"{current_time}_{random_number}"

async def change_hue(image, hue_shift):
    h = image.convert('HSV')
    h, s, v = h.split()
    if hue_shift < 0:
        hue_shift = (hue_shift * 0.8) * (180 / 255)
        h = h.point(lambda x: ((x + hue_shift ) % 256))
    elif hue_shift > 0:
        hue_shift = (hue_shift * 1.2) * (180 / 255)
        h = h.point(lambda x: ((x + hue_shift ) % 256))
    else:
        h = h.point(lambda x: ((x + hue_shift ) % 256))
    new_image = Image.merge('HSV', (h, s, v)).convert('RGBA')
    new_image.putalpha(image.getchannel('A'))
    return new_image

async def SaveImage(image, name):
    image.save(f"images/{name}")
    return

async def GetFish(location_id):
    fish = []
    for one_fish in data:
        locations = one_fish["catch_req"]["location_ids"]
        if int(location_id) in locations:
            fish.append(one_fish["name"])
    return fish

async def FishDetails(fish):
    for one_fish in data:
        try:
          name = one_fish["name"]
          if str(fish) == name:
              return one_fish
        except Exception as e:
          print(f"Error reading the data. Error: {e}")

async def GetFile(name: str, folder: str):
    if folder == "fish":
        name = name["id"]
    file_name = f"{name}.png"
    file_path = f"images/{folder}/{file_name}"
    file = discord.File(file_path, filename = file_name)
    return file

async def BuildFishEmbed(ctx: commands.Context, fish, image = None):
    fish_name = fish["name"]
    fish_id = fish["id"]
    fish_rating = ""
    for i in range(int(fish["rating"])):
        fish_rating += f"{Get.Emoji('star', 'others')} "
    fish_rarity_factor = float(fish["rarity_factor"])
    fish_catch_req = fish["catch_req"]
    fish_location = ""
    for location in fish_catch_req["location_ids"]:
        fish_location += f"{Get.LocationName(location)}\n"
    fish_baits = ""
    for bait in fish_catch_req["bait_category"]:
        fish_baits += f"{Get.Emoji(bait)} "
    fish_min_length = int(fish["min_length"]) + 1
    fish_avg_length = int(fish["avg_length"])
    fish_max_length = int(fish["max_length"]) - 1
    try:
        caught_time = fish_catch_req["caught_time"]
        fish_caught_time = ""
        for time in caught_time:
            fish_caught_time += f"{time}\n"
    except:
        fish_caught_time = "Always"
    try:
        caught_date = fish_catch_req["caught_date"]
        fish_caught_date = ""
        for date in caught_date:
            fish_caught_date += f"{FormatDate(date)}\n"
        fish_active = "No"
        for date in caught_date:
            if TodayIsInInterval(date):
                fish_active = "Yes"
    except:
        fish_caught_date = "Always"
        fish_active = "Yes"

    fish_price = fish["price"]
    fish_price_shiny = fish["price_shiny"]

    embed = discord.Embed(
        title = fish_name,
        description = "",
        color = discord.Colour.blurple(),

    )
    embed.set_author(name = bot.user.name, icon_url = bot.user.avatar.url)

    embed.add_field(name = "Rating:", value = f"{fish_rating} ({fish_rarity_factor:.2f})", inline = False)
    embed.add_field(name = "Location:", value = fish_location, inline = False)
    embed.add_field(name = "Baits:", value = fish_baits, inline = False)

    embed.add_field(name = "Min length:", value = fish_min_length, inline = True)
    embed.add_field(name = "Avg length:", value = fish_avg_length, inline = True)
    embed.add_field(name = "Max length:", value = fish_max_length, inline = True)

    embed.add_field(name = "Caught time:", value = fish_caught_time, inline = True)
    embed.add_field(name = "Caught date:", value = fish_caught_date, inline = True)
    embed.add_field(name = "Active: <:Season:1100778583741435996>", value = fish_active, inline = True)
    
    embed.add_field(name = "Price:", value = f"{fish_price} {Get.Emoji('fishbucks', 'others')}", inline = True)
    embed.add_field(name = "Price shiny:", value = f"{fish_price_shiny} {Get.Emoji('fishbucks', 'others')}", inline = True)
    
    if image is None:
        embed.set_image(url = f"attachment://{fish_id}.png")
    else:
        embed.set_image(url = f"attachment://{image}")

    author = ctx.author
    embed.set_footer(text = author, icon_url = author.avatar)
    return embed

async def BuildLocationsEmbed(ctx: commands.Context):
    embed = discord.Embed(
        title = "SELECT LOCATION",
        description = "",
        color = discord.Colour.blurple(),
    )
    embed.set_author(name = bot.user.name, icon_url = bot.user.avatar.url)

    embed.add_field(name = "Fishao username:", value = "Unknown", inline = True)
    embed.add_field(name = "Fish caught:", value = "0/615", inline = True)
    embed.add_field(name = "", value = "*:arrow_up: These features are coming soon!*", inline = False)
    embed.add_field(name = "Select location in dropdown menu.", value = "", inline = False)
    

    embed.set_image(url = f"attachment://world.png")

    author = ctx.author
    embed.set_footer(text = author, icon_url = author.avatar)

    return embed

async def BuildLocationEmbed(location: str, ctx: commands.Context):
    badge_id = Get.BadgeId(location)
    embed = discord.Embed(
        title = location,
        description = "",
        color = discord.Colour.blurple(),
    )
    embed.set_author(name = bot.user.name, icon_url = bot.user.avatar.url)

    embed.set_image(url = f"attachment://{badge_id}.png")

    author = ctx.author
    embed.set_footer(text = author, icon_url = author.avatar)

    return embed

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

async def BlockNonAuthorInteraction(interaction: discord.Interaction):
    message = f"{interaction.user.mention} you can't do that! Please don't ruin interactions created by other users.You can create you own using `/fishex`."
    await interaction.response.send_message(message, ephemeral=True, delete_after=30)

class LocationSelect(discord.ui.Select):
    def __init__(self, ctx):
        options = [discord.SelectOption(label=location,description="") for location in Get.LocationsList()]
        super().__init__(placeholder = "Select a location!", options = options, min_values = 1, max_values = 1)
        self.ctx = ctx

    async def callback(self, interaction): 
        fish = await GetFish(Get.LocationId(self.values[0]))
        if interaction.user.id == self.ctx.author.id:
            # External emoji bug interaction.response.edit_message()
            await interaction.message.delete()
            await interaction.channel.send(file = await GetFile(Get.BadgeId(self.values[0]), "badges"), embed = await BuildLocationEmbed(self.values[0], self.ctx), view=Fish(fish, self.ctx)) 
        else:
            await BlockNonAuthorInteraction(interaction)

class Location(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.add_item(LocationSelect(ctx))

    async def on_timeout(self):
        if self.message:
            self.clear_items()
            await self.message.edit(view=self)
        else:
            print("Message not found.")

class FishSelect(discord.ui.Select):
    def __init__(self, view, fish, ctx):
        self.ctx = ctx
        self.View = view
        self.select = self.View.get_item("fish_select")
        options = [discord.SelectOption(label=one_fish,description="") for one_fish in fish]
        super().__init__(placeholder = "Select a fish", options = options, min_values = 1, max_values = 1, custom_id="fish_select")

    async def callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            for custom_id in ["shiny", "default"]:
                button = self.View.get_item(custom_id)
                self.View.remove_item(button)
            fish = await FishDetails(self.values[0])
            self.View.selected_fish = fish
            self.View.add_item(ShinyButton(self.View, self.ctx))
            await interaction.response.edit_message(file = await GetFile(fish, "fish"), embed = await BuildFishEmbed(ctx = self.ctx, fish = fish), view = self.View)
        else:
            await BlockNonAuthorInteraction(interaction)

class PreviousButton(discord.ui.Button):
    def __init__(self, fish_view: discord.ui.View, ctx):
        self.fish_view = fish_view
        self.ctx = ctx
        super().__init__(label="Previous page", disabled=True, custom_id="previous")

    
    async def callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.fish_view.page -= 1
            if self.fish_view.page == 0:
                self.disabled = True
            self.fish_view.get_item("next").disabled = False
            new_options = [
                discord.SelectOption(label=fish, description="")
                for fish in self.fish_view.pages[self.fish_view.page]
            ]
            self.fish_view.get_item("fish_select").options.clear()
            self.fish_view.get_item("fish_select").options.extend(new_options)
            await interaction.response.edit_message(view=self.fish_view)
        else:
            await BlockNonAuthorInteraction(interaction)

class NextButton(discord.ui.Button):
    def __init__(self, fish_view: discord.ui.View, ctx):
        super().__init__(label="Next page", custom_id="next")
        self.fish_view = fish_view
        self.ctx = ctx
    
    async def callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.fish_view.page += 1
            if self.fish_view.page == (len(self.fish_view.pages) - 1):
                self.disabled = True
            self.fish_view.get_item("previous").disabled = False
            new_options = [
                discord.SelectOption(label=fish, description="")
                for fish in self.fish_view.pages[self.fish_view.page]
            ]
            self.fish_view.get_item("fish_select").options.clear()
            self.fish_view.get_item("fish_select").options.extend(new_options)
            await interaction.response.edit_message(view=self.fish_view)
        else:
            await BlockNonAuthorInteraction(interaction)

class BackButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="Back", custom_id="back")
        self.ctx = ctx
    
    async def callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            await interaction.response.edit_message(file = await GetFile("world", "resources"), embed = await BuildLocationsEmbed(self.ctx), view = Location(self.ctx))
        else:
            await BlockNonAuthorInteraction(interaction)

class ShinyButton(discord.ui.Button):
    def __init__(self, view, ctx):
        super().__init__(label="Shiny", custom_id="shiny")
        self.View = view
        self.ctx = ctx

    async def callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            shiny_button = self.View.get_item("shiny")
            self.View.remove_item(shiny_button)
            self.View.add_item(DefaultButton(self.View, self.ctx))
            selected_fish_id = self.View.selected_fish["id"]
            selected_fish_hue = int(self.View.selected_fish["hue_shift_of_shiny"])
            image_name = f"temp_image_{await FileCoding()}.png"
            image = await change_hue(Image.open(f"images/fish/{selected_fish_id}.png"), selected_fish_hue)
            await SaveImage(image, image_name)
            await interaction.response.edit_message(file = discord.File(f"images/{image_name}"), embed = await BuildFishEmbed(ctx = self.ctx, fish = self.View.selected_fish, image = image_name), view = self.View)
            os.remove(f"images/{image_name}")
        else:
            await BlockNonAuthorInteraction(interaction)

class DefaultButton(discord.ui.Button):
    def __init__(self, view, ctx):
        super().__init__(label="Default", custom_id="default")
        self.View = view
        self.ctx = ctx

    async def callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            default_button = self.View.get_item("default")
            self.View.remove_item(default_button)
            self.View.add_item(ShinyButton(self.View, self.ctx))
            await interaction.response.edit_message(file = await GetFile(self.View.selected_fish, "fish"), embed = await BuildFishEmbed(ctx = self.ctx, fish = self.View.selected_fish), view = self.View)
        else:
            await BlockNonAuthorInteraction(interaction)

class Fish(discord.ui.View):
    def __init__(self, fish, ctx):
        super().__init__()
        fish_list = sorted(fish)
        self.selected_fish = None
        if len(fish_list) > 25:
            self.fish = fish_list[0:25]
            self.pages = split_list(fish_list)
            self.page = 0
            self.add_item(FishSelect(self, self.fish, ctx))
            self.add_item(PreviousButton(self, ctx))
            self.add_item(NextButton(self, ctx))
        else:
            self.fish = fish_list
            self.add_item(FishSelect(self, self.fish, ctx))
        self.add_item(BackButton(ctx))

    async def on_timeout(self):
        if self.message:
            self.clear_items()
            await self.message.edit(view=self)
        else:
            print("Message not found.")

@bot.slash_command()
async def fishdex(ctx: commands.Context):
    current_date_time: datetime.datetime = datetime.datetime.now()
    formated_date_time: str = current_date_time.strftime("%d.%m.%Y | %H:%M:%S")
    user: str = ctx.author.name
    print(f"{formated_date_time} | {user} used command fishdex")
    await ctx.response.defer()
    await ctx.followup.send(file = await GetFile("world", "resources"), embed = await BuildLocationsEmbed(ctx), view=Location(ctx))

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        return 
    raise error

bot.run(API_KEY)