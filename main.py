import discord
from discord import ButtonStyle, Embed, Interaction
from discord.ext import commands, tasks
import os
import json
from datetime import datetime, timedelta
from discord.ui import View, Button
from discord.utils import get
import random
from keep_alive import keep_alive
from replit import db
import asyncio
from collections import Counter, deque

# Key names in Replit DB
PREMIUM_USERS_KEY = "premium_users"
JOURNAL_KEY = "dream_journal"

# Load premium users from Replit DB
def load_premium_users():
    return db.get(PREMIUM_USERS_KEY, {})

# Save premium users to Replit DB
def save_premium_users(premium_users):
    db[PREMIUM_USERS_KEY] = premium_users

# Initialize premium users
def init_premium_users():
    if PREMIUM_USERS_KEY not in db:
        save_premium_users({})
    return load_premium_users()

# Load dream journal from Replit DB
def load_journal():
    return db.get(JOURNAL_KEY, {})

# Save dream journal to Replit DB
def save_journal(journal):
    db[JOURNAL_KEY] = journal

# Load existing premium users and journal
premium_users = init_premium_users()
dream_journal = load_journal()

# Define bot with prefix
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix="d!", intents=intents)
client.remove_command("help")

# Event triggered when the bot joins a guild
    # Event triggered when the bot joins a guild
@client.event
async def on_guild_join(guild):
    print(f"Joined a new server: {guild.name}")

    # Find channels that have 'chat' (case-insensitive) in their name
    channels = [channel for channel in guild.text_channels if 'chat' or 'general' in channel.name.lower()]
    print(f"Channels found with 'chat' in their name: {[channel.name for channel in channels]}")

    if not channels:
        print("No channels found with 'chat' in the name.")
        return  # No channel found with "chat" in its name

    # Select the first channel found with "chat" in its name
    target_channel = channels[0]
    print(f"Sending message to {target_channel.name}")

    # Create the welcome message embed with a creative, attractive design
    embed = discord.Embed(
        title="🎉 **Welcome to the Server!** 🎉",
        description=(
            "Hey there, we're thrilled to have you join us! 😸\n\n"
            "Before you dive in, here's a quick guide to get started:\n\n"
            "1. **Prefix:** All commands start with `d!` (e.g., `d!help`).\n"
            "2. **Help Command:** Type `d!help` to see a list of available commands.\n"
            "3. **Introduce Yourself:** Say hello in the chat or share your dreams with us!\n\n"
            "Don't forget, if you ever need assistance, just reach out to any member or check out the help commands! 🗨️"
        ),
        color=0x973DA4  # Your custom purple hex code
    )
    embed.set_thumbnail(url=guild.me.display_avatar.url)  # Optional image for the welcome message
    embed.set_footer(text="Type `d!help` to get started!")

    # Define a delete button
    class DeleteButton(View):
        def __init__(self):
            super().__init__(timeout=None)  # Button will persist indefinitely

        @discord.ui.button(label="Delete 🗑️", style=discord.ButtonStyle.danger)
        async def delete_button(self, interaction: discord.Interaction, button: Button):
            """Handles the delete button press"""
            await interaction.response.send_message("The welcome message will be deleted.", ephemeral=True)
            await embed_message.delete()  # Delete the message

    # Create the view and button
    view = DeleteButton()

    # Send the welcome message in the first channel found with "chat" in its name
    embed_message = await target_channel.send(embed=embed, view=view)
    print("Welcome message sent successfully.")

dream_symbols = {
    "Falling": "Symbolizes loss of control or fear of failure.",
    "Flying": "Represents freedom and overcoming challenges.",
    "Being Chased": "Reflects anxiety or avoiding issues.",
    "Teeth Falling Out": "Signifies insecurity or fear of aging.",
    "Water": "Represents emotional state.",
    "Death": "Symbolizes transformation or endings.",
    "Nudity": "Represents vulnerability or authenticity.",
    "Flying or Falling in an Elevator": "Symbolizes emotional shifts or instability.",
    "Being Late": "Indicates fear of missing opportunities.",
    "Driving a Car": "Represents control or lack of direction.",
    "Losing Something": "Signifies insecurity or fear of loss.",
    "Flying High": "Represents ambition and success.",
    "Snakes": "Symbolizes fear, danger, or transformation.",
    "Being Trapped": "Represents feeling stuck or restricted.",
    "Meeting a Celebrity": "Represents admiration or aspirations.",
    "Finding Money": "Symbolizes self-worth and opportunities.",
    "Losing Teeth": "Signifies communication issues or insecurity.",
    "Being in School": "Represents learning or personal growth.",
    "Fighting": "Reflects inner conflict or suppressed anger.",
    "House": "Symbolizes self or aspects of personality.",
    "Rain": "Represents renewal or emotional release.",
    "Being Lost": "Signifies confusion or lack of direction.",
    "Climbing": "Represents progress or ambition.",
    "Meeting a Stranger": "Symbolizes unknown aspects or new opportunities.",
    "Storms": "Represents emotional turmoil or conflict.",
    "Animals": "Represents instincts or specific traits.",
    "Mountains": "Represents challenges or spiritual growth.",
    "Fire": "Symbolizes transformation or passion.",
    "Baby": "Represents new beginnings or vulnerability.",
    "Exams": "Reflects stress or self-assessment.",
    "Being Paralyzed": "Represents feeling stuck or powerless.",
    "Food": "Represents nourishment or desires.",
    "Shadow": "Symbolizes hidden aspects or fears.",
    "Walking Through a Door": "Represents transition or new opportunities.",
    "Broken Objects": "Represents loss or need for repair.",
    "Colors": "Represents emotional or symbolic meanings.",
    "Running": "Represents urgency or striving for goals.",
    "Keys": "Represents solutions or opportunities.",
    "Stairs": "Represents progress or a journey.",
    "Mirror": "Symbolizes self-reflection or identity.",
    "Darkness": "Represents fear or uncertainty.",
    "Rainbows": "Represents hope or resolution.",
    "Bags or Luggage": "Represents burdens or responsibilities.",
    "Gardens": "Represents growth or creativity.",
    "Hair": "Represents strength or identity.",
    "Clocks": "Represents time or urgency.",
    "Bridges": "Represents transition or overcoming obstacles.",
    "Ocean": "Symbolizes vast emotions or the unconscious mind.",
    "Stars": "Represents hope, guidance, or inspiration.",
    "Wings": "Symbolizes freedom, ambition, or spirituality."
}

premium_dream_symbols = {
    "Falling": "Falling in dreams often indicates a sense of loss of control in your waking life. It can symbolize feelings of fear, insecurity, or failure. This type of dream may also suggest a need to let go of certain anxieties or situations that are weighing you down, prompting self-reflection and reassessment of priorities.",
    "Flying": "Flying dreams are usually positive and reflect a sense of freedom, empowerment, and triumph over obstacles. They can signify a desire to break free from limitations or an indication that you are achieving your goals. The sensation of flight may also point to a higher perspective or spiritual journey.",
    "Being Chased": "Dreaming of being chased often reflects unresolved fears, anxieties, or avoidance of an issue in waking life. It suggests that you might be running away from something important, whether it is a responsibility, a confrontation, or a hidden fear that requires attention.",
    "Teeth Falling Out": "Dreams of teeth falling out are frequently associated with feelings of vulnerability, insecurity, or concerns about appearance and aging. They may also relate to fears of losing control, communication issues, or anxieties about how you are perceived by others.",
    "Water": "Water in dreams is deeply symbolic, often reflecting emotional states. Calm waters may signify peace and tranquility, while turbulent waters could represent emotional chaos or uncertainty. Water can also symbolize renewal, cleansing, and the subconscious mind.",
    "Death": "Dreams about death rarely indicate literal death but are more about transformation and endings. They signify major life changes, the closure of a chapter, or the beginning of something new. Such dreams often encourage self-reflection and adaptation to change.",
    "Nudity": "Being naked in a dream can reveal feelings of vulnerability, embarrassment, or exposure. Alternatively, it may symbolize authenticity, freedom, and a desire to be true to oneself without pretense or fear of judgment.",
    "Flying or Falling in an Elevator": "Elevator dreams often reflect emotional ups and downs or transitions in life. Flying upward may symbolize progress, ambition, or rising above challenges, while falling may indicate fears of failure, instability, or loss of control.",
    "Being Late": "Dreams of being late typically stem from anxiety about missing opportunities or not living up to expectations. They may also highlight feelings of unpreparedness or the pressure to meet deadlines and responsibilities.",
    "Driving a Car": "Driving a car in a dream is a metaphor for control over your life’s direction. Smooth driving may indicate confidence and self-assurance, while reckless or out-of-control driving suggests a lack of focus or difficulties in managing responsibilities.",
    "Losing Something": "Dreams about losing something often reflect feelings of insecurity, fear, or the potential loss of something valuable in life, such as relationships, opportunities, or personal identity. They may prompt introspection to identify what feels lacking or threatened.",
    "Flying High": "Dreaming of flying high is a symbol of ambition, confidence, and the ability to overcome challenges. It reflects a sense of achievement and personal growth, encouraging you to reach for your aspirations.",
    "Snakes": "Snakes in dreams can have diverse meanings, ranging from hidden fears and dangers to transformation and healing. They may represent something in your life that is unpredictable or something that requires attention and resolution.",
    "Being Trapped": "Dreams of being trapped often symbolize feeling stuck, restricted, or powerless in waking life. They may indicate a need to evaluate situations or relationships that limit your freedom and seek ways to break free.",
    "Meeting a Celebrity": "Dreaming of a celebrity often reflects admiration for certain qualities or aspirations to achieve similar recognition or success. It may also symbolize the desire to embody traits you associate with the celebrity.",
    "Finding Money": "Finding money in a dream symbolizes self-worth, hidden talents, and unexpected opportunities. It reflects a sense of abundance and may encourage you to recognize your own value and potential.",
    "Losing Teeth": "This dream often represents communication issues, insecurities, or fears of aging and powerlessness. It may suggest the need to confront anxieties related to self-expression or confidence.",
    "Being in School": "Dreams of being in school often relate to personal growth, learning, or unresolved issues from past educational experiences. They may symbolize the pursuit of knowledge, self-improvement, or social interactions.",
    "Fighting": "Dreams of fighting often indicate inner conflict, unresolved anger, or a struggle to assert oneself in waking life. They may highlight the need to address suppressed emotions or confront challenges head-on.",
    "House": "Dreaming of a house often symbolizes the self and its various aspects. Different rooms may represent different facets of your personality, emotions, or areas of life requiring attention and care.",
    "Rain": "Rain in dreams often symbolizes renewal, cleansing, and emotional release. It may signify the end of a difficult phase, the start of something new, or the expression of suppressed emotions.",
    "Being Lost": "This dream reflects feelings of confusion, uncertainty, or a lack of direction in life. It may point to a need for self-discovery, grounding, or clarifying your goals and priorities.",
    "Climbing": "Dreaming of climbing represents effort, determination, and progress toward goals. It may indicate ambition or the challenges you face while striving for success.",
    "Meeting a Stranger": "Strangers in dreams often symbolize unknown aspects of yourself, potential opportunities, or fears of the unfamiliar. They may represent something new entering your life.",
    "Storms": "Storms in dreams often represent emotional turmoil, conflict, or intense situations. They may indicate the need to weather difficult circumstances or the release of pent-up feelings.",
    "Animals": "Dreams of animals symbolize instincts, desires, or specific traits associated with the animal. For instance, a lion may signify courage, while a bird could represent freedom.",
    "Mountains": "Mountains in dreams often symbolize challenges, achievements, or spiritual growth. Climbing a mountain suggests perseverance and overcoming obstacles, while observing one may reflect admiration or inspiration.",
    "Fire": "Fire in dreams can symbolize transformation, passion, or destruction. It may reflect intense emotions, a burning desire for change, or the need to let go of something to start anew.",
    "Baby": "Dreaming of a baby often represents new beginnings, innocence, or vulnerability. It may symbolize a fresh start or something in its early developmental stages that requires nurturing.",
    "Exams": "Dreaming of exams often reflects stress, self-assessment, or fears of judgment. It may indicate the need to evaluate your performance or prepare for challenges in waking life.",
    "Being Paralyzed": "Dreams of paralysis often signify feeling stuck, powerless, or unable to move forward in life. They may also relate to fear, anxiety, or a sense of being overwhelmed by circumstances.",
    "Food": "Food in dreams often symbolizes nourishment, desires, or abundance. It may reflect emotional or physical needs, the pursuit of satisfaction, or a craving for fulfillment.",
    "Shadow": "Shadows in dreams often represent hidden aspects of the self, unresolved fears, or repressed emotions. They may encourage self-reflection and the integration of overlooked traits.",
    "Walking Through a Door": "Dreaming of walking through a door often symbolizes transition, opportunities, or new phases in life. It may reflect a desire for change or the opening of new possibilities.",
    "Broken Objects": "Dreaming of broken objects often symbolizes loss, disappointment, or feelings of inadequacy. They may suggest a need to address unresolved issues or repair something in your life.",
    "Colors": "Specific colors in dreams carry symbolic meanings. For example, red may indicate passion or anger, blue might symbolize calmness or communication, and green often represents growth or healing.",
    "Running": "Dreams of running often signify urgency, determination, or the pursuit of goals. They may also reflect a desire to escape or move quickly through challenging situations.",
    "Keys": "Keys in dreams often symbolize solutions, opportunities, or access to new possibilities. They may suggest unlocking potential or finding answers to problems.",
    "Stairs": "Dreaming of stairs often represents progress, growth, or a journey toward a goal. Ascending may indicate achievement, while descending could symbolize introspection or regression.",
    "Mirror": "Mirrors in dreams symbolize self-reflection, identity, or perception. They may encourage you to examine how you see yourself or how others perceive you.",
    "Darkness": "Darkness in dreams often represents fear, uncertainty, or the unknown. It may highlight feelings of being lost or the need to find clarity and understanding.",
    "Rainbows": "Rainbows in dreams often symbolize hope, resolution, and the promise of better times. They may reflect the overcoming of challenges and the reward of perseverance.",
    "Bags or Luggage": "Dreams of bags or luggage often symbolize burdens, responsibilities, or the emotional weight you carry. They may indicate a need to unpack and address unresolved issues.",
    "Gardens": "Gardens in dreams often symbolize growth, creativity, and nurturing. They may reflect personal development, the cultivation of ideas, or a desire for harmony.",
    "Hair": "Dreams of hair often represent strength, identity, or personal power. The state of the hair may reflect self-esteem, vitality, or how you view yourself.",
    "Clocks": "Clocks in dreams often symbolize time, urgency, or the passage of life. They may suggest a need to manage time better or highlight feelings of pressure or deadlines.",
    "Bridges": "Dreaming of bridges often symbolizes transition, connection, or overcoming obstacles. They may reflect a journey from one phase of life to another or the bridging of differences.",
    "Ocean": "The ocean in dreams often symbolizes vast emotions, the subconscious mind, or infinite possibilities. It may reflect emotional depth, a desire for exploration, or feelings of awe and mystery.",
    "Stars": "Stars in dreams often symbolize hope, guidance, or inspiration. They may reflect aspirations, dreams, or a sense of connection to the larger universe.",
    "Wings": "Wings in dreams often symbolize freedom, ambition, or spirituality. They may reflect a desire to rise above limitations, achieve higher goals, or explore new horizons."
}

def interpret_dream(dream, premium=False):
    interpretations = []
    symbols = premium_dream_symbols if premium else dream_symbols

    for symbol, meaning in symbols.items():
        if symbol.lower() in dream.lower():
            interpretations.append(f"**{symbol}**: {meaning}")

    if not interpretations:
        interpretations.append("I couldn't find a symbol in your dream to interpret. Try being more descriptive!")

    return "\n".join(interpretations)

@client.command()
async def dream(ctx, *, dream_description: str):
    """Interpret a dream description."""
    is_premium = str(ctx.author.id) in premium_users
    interpretation = interpret_dream(dream_description, premium=is_premium)

    embed = discord.Embed(
        title="Dream Interpretation",
        color=discord.Color.gold() if is_premium else 0x973DA4
    )
    embed.add_field(name="Your Dream", value=dream_description, inline=False)
    embed.add_field(name="Interpretation", value=interpretation, inline=False)
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg"
        if is_premium else ctx.me.display_avatar.url
    )

    if is_premium:
        embed.add_field(
            name="Premium Insights",
            value="As a premium user, you enjoy detailed and personalized dream analysis.",
            inline=False,
        )
        # Save dream to journal
        if str(ctx.author.id) not in dream_journal:
            dream_journal[str(ctx.author.id)] = []
        dream_journal[str(ctx.author.id)].append({
            "dream": dream_description,
            "interpretation": interpretation,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        save_journal(dream_journal)
    else:
        embed.set_footer(text="Upgrade to premium for more valuable insights! ")

    await ctx.send(embed=embed)

# Error Handler for the 'dream' command
@dream.error
async def dream_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Dream Command Error",
            description="_You must provide a dream description for interpretation._ ⚠️\n"
                        "Usage: `!dream <your dream>`",
            color=0x973DA4
        )
        embed.set_footer(text="Try again with a detailed dream description! ⚠️")
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="Dream Command Error",
            description="_Invalid argument provided. Please use the correct format._ ⚠️\n"
                        "Usage: `!dream <your dream>`",
            color=0x973DA4
        )
        await ctx.send(embed=embed)
    else:
        # Handle unexpected errors
        embed = discord.Embed(
            title="Unexpected Error",
            description="_An unexpected error occurred while processing your dream. Please try again later._ ⚠️",
            color=0x973DA4
        )
        await ctx.send(embed=embed)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    check_premium_expiry.start()
    activity = discord.Activity(type=discord.ActivityType.listening, name="d!help")
    await client.change_presence(status=discord.Status.online, activity=activity)

    # Command to add a user to premium
@client.command()
@commands.is_owner()  # Restrict access to the bot owner
async def add_premium(ctx, user: discord.User, days: int):
    """Add a user to premium with a specified duration."""
    try:
        # Calculate expiration date
        expiration_date = datetime.now() + timedelta(days=days)
        premium_users[str(user.id)] = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
        save_premium_users(premium_users)
    
        # Success message
        embed = discord.Embed(
            description=f"Added {user.mention} to premium for {days} days.",
            color=0x973DA4
        )
        embed.set_thumbnail(url=ctx.me.display_avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        # Handle unexpected errors
        embed = discord.Embed(
            description=f"An error occurred: {str(e)}",
            color=0xFF0000
        )
        await ctx.send(embed=embed)

    # Error handler for the add_premium command
@add_premium.error
async def add_premium_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # Non-owner tried to use the command
        embed = discord.Embed(
            description="_You don't have permission to use this command. Only the bot owner can perform this action_ ⚠️",
            color=0x973DA4
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        # Missing arguments
        embed = discord.Embed(
            description="_Usage: `d!add_premium <user> <days>`\nMake sure to specify both the user and the number of days_ ⚠️",
            color=0x973DA4
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        # Invalid argument type
        embed = discord.Embed(
            description="_Invalid argument. Please provide a valid user and number of days_ ⚠️",
            color=0x973DA4
        )
        await ctx.send(embed=embed)
    else:
        # Other errors
        embed = discord.Embed(
            description="_An unexpected error occurred. Please try again_ ⚠️",
            color=0x973DA4
        )
        await ctx.send(embed=embed)

@client.command()
async def view_premium(ctx):
    """View all premium users and their expiration dates."""
    if not premium_users:
        await ctx.send("```No premium users found ❌```")
        return
    
    embed = discord.Embed(
        title="Premium Users 💎",
        color=discord.Color.gold(),
        description="List of users with premium access and their expiration dates."
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg")
    
    # Iterate through premium users
    for user_id, expiration_str in premium_users.items():
        try:
            # Fetch user and parse expiration time
            user = await client.fetch_user(user_id)
            expiration = datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S")
            remaining_time = expiration - datetime.now()
    
            if remaining_time.total_seconds() > 0:
                days, hours, minutes = (
                    remaining_time.days,
                    remaining_time.seconds // 3600,
                    (remaining_time.seconds % 3600) // 60,
                )
                countdown = f"{days}d {hours}h {minutes}m"
                status = f"Expires on: {expiration_str} ⏳\nTime left: **{countdown}**"
            else:
                status = "Expired ❌"
    
            # Add user info to embed
            embed.add_field(name=user.name, value=status, inline=False)
    
        except Exception as e:
            # Handle errors fetching user data
            embed.add_field(
                name=f"User ID: {user_id}",
                value="Unable to fetch user details. Possibly invalid user ID.",
                inline=False
            )
    
    await ctx.send(embed=embed)

@client.command()
async def premium_features(ctx):
    """Showcase premium features in an embed."""
    embed = discord.Embed(title="Premium Features", color=0x973DA4)
    embed.add_field(name="Advanced Dream Analysis", value="Unlock deeper and more personalized insights into your dreams.", inline=False)
    embed.add_field(name="Dream Journaling", value="Keep a record of your interpreted dreams and revisit them anytime.", inline=False)
    embed.add_field(name="Priority Support", value="Get quicker responses to your queries and suggestions.", inline=False)
    embed.set_thumbnail(url = ctx.me.display_avatar.url)
    embed.set_footer(text="Contact Bot's Admin to avail the premium features.")
    await ctx.send(embed=embed)

@tasks.loop(minutes=1)
async def check_premium_expiry():
    """Check and remove expired premium users."""
    global premium_users
    now = datetime.now()

    if not isinstance(premium_users, dict):
        premium_users = {}
        save_premium_users(premium_users)

    expired_users = [user_id for user_id, exp in premium_users.items() if datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") < now]

    for user_id in expired_users:
        del premium_users[user_id]

    if expired_users:
        save_premium_users(premium_users)

        # Bot command to remove premium status
@client.command()
@commands.is_owner()  # Restricts access to the bot owner
async def remove_premium(ctx, user: discord.User):
    """Manually remove a user's premium status."""
    user_id_str = str(user.id)
    
    if user_id_str in premium_users:
        del premium_users[user_id_str]
        save_premium_users(premium_users)
    
        # Success message
        embed = discord.Embed(
            description=f"{user.mention} has been removed from the premium.",
            color=0x973DA4
        )
        embed.set_thumbnail(url=ctx.me.display_avatar.url)
        await ctx.send(embed=embed)
    else:
        # User not found message
        embed = discord.Embed(
            description=f"{user.mention} is not a premium user.",
            color=0x973DA4
        )
        embed.set_thumbnail(url=ctx.me.display_avatar.url)
        embed.set_footer(text="Use d!add_premium to add a user to premium.")
        await ctx.send(embed=embed)

# Custom error handler for commands
@remove_premium.error
async def remove_premium_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # Non-owner tried to use the command
        embed = discord.Embed(
            description="_You don't have permission to use this command. Only the bot owner can perform this action_ ⚠️",
            color=0x973DA4
        )
        embed.set_thumbnail(url=ctx.me.display_avatar.url)
        await ctx.send(embed=embed)
    else:
        # Handle other errors (optional)
        embed = discord.Embed(
            description="_An error occurred while processing the command_ ⚠️",
            color=0x973DA4
        )
        await ctx.send(embed=embed)
        
@client.command()
async def journal(ctx):
    """Guide the user through journaling their dream reflections."""
    if str(ctx.author.id) not in premium_users:
        await ctx.send("```This feature is only available for premium users.\nUse d!owner to contact the owner 😸```")
        return

    await ctx.send("```Let's begin journaling your dream reflections 😸```")
    await asyncio.sleep(3)
    # Prompt for dream description
    embed = discord.Embed(
        title="Dream Journaling",
        description="Describe your dream in detail:",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg?ex=67863816&is=6784e696&hm=7e2a60ae72dad81a793c440a21fad73193aaec67a35d4eb35626fd340960db55&")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        dream_msg = await client.wait_for("message", check=check, timeout=120.0)
        dream_description = dream_msg.content
    except asyncio.TimeoutError:
        await ctx.send("```You took too long to respond. Please try again later ⚠️```")
        return

    # Prompt for interpretation
    embed = discord.Embed(
        title="Dream Interpretation",
        description="What is your interpretation of this dream?",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg?ex=67863816&is=6784e696&hm=7e2a60ae72dad81a793c440a21fad73193aaec67a35d4eb35626fd340960db55&")
    await ctx.send(embed=embed)

    try:
        interpretation_msg = await client.wait_for("message", check=check, timeout=120.0)
        interpretation = interpretation_msg.content
    except asyncio.TimeoutError:
        await ctx.send("```You took too long to respond. Please try again later ⚠️```")
        return

    # Prompt for reflection questions
    questions = [
        "What emotions did this dream evoke?",
        "Did any part of the dream feel particularly significant?",
        "How does this dream relate to your current life situation?"
    ]

    responses = []
    for question in questions:
        embed = discord.Embed(title="Dream Journaling", description=question, color=discord.Color.gold())
        embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg?ex=67863816&is=6784e696&hm=7e2a60ae72dad81a793c440a21fad73193aaec67a35d4eb35626fd340960db55&")
        await ctx.send(embed=embed)

        try:
            msg = await client.wait_for("message", check=check, timeout=60.0)
            responses.append(msg.content)
        except asyncio.TimeoutError:
            await ctx.send("```You took too long to respond. This question will be marked as unanswered ⚠️```")
            responses.append("No response.")

    if str(ctx.author.id) not in dream_journal:
        dream_journal[str(ctx.author.id)] = []

    journal_entry = {
        "dream": dream_description,
        "interpretation": interpretation,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reflection": responses
    }
    dream_journal[str(ctx.author.id)].append(journal_entry)
    save_journal(dream_journal)

    embed = discord.Embed(
        description="Your dream reflections have been journaled ✅",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg?ex=67863816&is=6784e696&hm=7e2a60ae72dad81a793c440a21fad73193aaec67a35d4eb35626fd340960db55&")
    await ctx.send(embed=embed)

@client.command()
async def view_journal(ctx):
    """View all journal entries."""
    if str(ctx.author.id) not in premium_users:
        await ctx.send("```This feature is only available for premium users.\nUse d!owner to contact the owner 😸```")
        return

    if str(ctx.author.id) not in dream_journal or not dream_journal[str(ctx.author.id)]:
        await ctx.send("```You have no journal entries ⚠️```")
        return

    entries = dream_journal[str(ctx.author.id)]
    embed = discord.Embed(
        title="Your Dream Journal Entries",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg?ex=67863816&is=6784e696&hm=7e2a60ae72dad81a793c440a21fad73193aaec67a35d4eb35626fd340960db55&")

    for idx, entry in enumerate(entries, start=1):
        # Construct a summary for each entry
        summary = (
            f"**Date:** {entry.get('date', 'Unknown')}\n"
            f"**Dream:** {entry.get('dream', 'No dream recorded')}\n"
            f"**Interpretation:** {entry.get('interpretation', 'No interpretation recorded')}\n"
            f"**Reflections:** {'; '.join(entry.get('reflection', ['No reflections recorded']))}"
        )
        embed.add_field(name=f"Entry #{idx}", value=summary, inline=False)

    await ctx.send(embed=embed)

@client.command()
async def clear_journal(ctx):
    """Clear all entries from your dream journal."""
    if str(ctx.author.id) not in premium_users:
        await ctx.send("```This feature is only available for premium users.\nUse d!owner to contact the owner 😸```")
        return

    if str(ctx.author.id) in dream_journal:
        del dream_journal[str(ctx.author.id)]
        save_journal(dream_journal)
        r = discord.Embed(description="Your dream journal has been cleared.", color = discord.Color.gold())
        r.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg?ex=67863816&is=6784e696&hm=7e2a60ae72dad81a793c440a21fad73193aaec67a35d4eb35626fd340960db55&")
        await ctx.send(embed=r)
    else:
        o = discord.Embed(description="You don't have any entries in your dream journal yet.", color = discord.Color.gold())
        o.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg?ex=67863816&is=6784e696&hm=7e2a60ae72dad81a793c440a21fad73193aaec67a35d4eb35626fd340960db55&")
        await ctx.send(embed=o)

@client.command()
async def clear_entry(ctx, entry_number: int):
    """Clear a specific entry from your dream journal."""
    if str(ctx.author.id) not in premium_users:
        await ctx.send("```This feature is only available for premium users.\nUse d!owner to contact the owner 😸```")
        return

    if str(ctx.author.id) in dream_journal:
        entries = dream_journal[str(ctx.author.id)]
        if 0 <= entry_number - 1 < len(entries):
            deleted_entry = entries.pop(entry_number - 1)
            save_journal(dream_journal)
            embed = discord.Embed(description=f"Entry #{entry_number} has been deleted", color=discord.Color.gold())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg")
            await ctx.send(embed=embed)
        else:
            e = discord.Embed(description=f"Invalid entry number. Please choose a valid entry from 1 to {len(entries)}.", color=discord.Color.gold())
            e.set_thumbnail(url="https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg")
            await ctx.send(embed=e)
    else:
        a = discord.Embed(description="You don't have any entries in your dream journal yet.", color=discord.Color.gold())
        a.set_thumbnail(url="https://cdn.discordapp.com/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg")
        await ctx.send(embed=a)

# Error Handler for the 'clear_entry' command
@clear_entry.error
async def clear_entry_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Clear Entry Command Error",
            description="You must provide the entry number to delete.\nUsage: `!clear_entry <entry_number>`",
            color=0x973DA4
        )
        embed.set_footer(text="Provide a valid entry number to delete from your dream journal.")
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="Clear Entry Command Error",
            description="The entry number must be an integer.\nUsage: `!clear_entry <entry_number>`",
            color=0x973DA4
        )
        await ctx.send(embed=embed)
    else:
        # Catch all other errors
        embed = discord.Embed(
            title="Unexpected Error",
            description="An unexpected error occurred while processing your request. Please try again later.",
            color=0x973DA4
        )
        await ctx.send(embed=embed)


@client.command()
async def suggest(ctx, *, suggestion: str):
    """Allows users to send suggestions to a specific channel."""
    # Replace with your suggestion channel ID
    suggestion_channel_id = 1329368955021950997  # Replace with the channel's ID
    suggestion_channel = client.get_channel(suggestion_channel_id)
    
    if suggestion_channel is None:
        await ctx.send("*❌ Suggestion channel not found. Please contact an admin.*")
        return
    
    # Create an embed for the suggestion
    embed = discord.Embed(
        title="New Suggestion",
        description=suggestion,
        color=0x973DA4,
        timestamp=ctx.message.created_at
    )
    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
    
    # Send the suggestion to the designated channel
    await suggestion_channel.send(embed=embed)
    
    # Acknowledge the suggestion to the user
    await ctx.send("*✅ Your suggestion has been submitted successfully!*")

# Error Handler for the 'suggest' command
@suggest.error
async def suggest_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="*💬 Suggest Command Error*",
            description="*You must provide a suggestion. Please try again.*\nUsage: `!suggest <your suggestion>`",
            color=0x973DA4
        )
        embed.set_footer(text="Make sure your suggestion is clear and concise!")
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="*💬 Suggest Command Error*",
            description="*Invalid argument provided. Please ensure your suggestion is properly formatted.*\nUsage: `!suggest <your suggestion>`",
            color=0x973DA4
        )
        await ctx.send(embed=embed)
    else:
        # Catch all other errors
        embed = discord.Embed(
            title="*⚠️ Unexpected Error*",
            description="*An unexpected error occurred while processing your suggestion. Please try again later.*",
            color=0x973DA4
        )
        await ctx.send(embed=embed)


@client.command()
async def pay_respect(ctx):
    """Pay respects using a button."""
    # Replace with your respect channel ID
    respect_channel_id = 1329767060267466792  # Replace with the channel's ID
    respect_channel = client.get_channel(respect_channel_id)

    if respect_channel is None:
        await ctx.send("```Respect channel not found. Please contact an admin ⚠️```")
        return

    class RespectButton(View):
        def __init__(self):
            super().__init__(timeout=None)  # Button will persist indefinitely
            self.respects_count = 0

        @discord.ui.button(label="F", style=discord.ButtonStyle.blurple)
        async def pay_respect_button(self, interaction: discord.Interaction, button: Button):
            """Handles the button click to pay respect."""
            # Increment the respect count
            self.respects_count += 1

            # Acknowledge the user's click
            await interaction.response.send_message(f"Thank you for paying respect, {interaction.user.display_name}.", ephemeral=True)

            # Disable the button after it is clicked
            button.disabled = True
            await interaction.message.edit(view=self)  # Re-edit the message to apply the disabled button

            # Send the updated respect count to the channel
            await respect_channel.send(
                embed=discord.Embed(
                    title="Respect Paid",
                    description=(
                        f"{interaction.user.display_name} has paid their respect.\n"
                        f"Total respects paid: **{self.respects_count}**"
                    ),
                    color=0x973DA4
                )
            )

    # Create an embed for the initial message
    embed = discord.Embed(
        title="Pay Respect",
        description="Click the button below to pay your respect. Your acknowledgment will be recorded.",
        color=0x973DA4
    )

    # Create and send the embed with the button view
    view = RespectButton()
    await ctx.send(embed=embed, view=view)

TRIVIA_FILE = "trivia_questions.txt"  # Path to trivia file

# Helper function to load trivia questions from file
def load_trivia_questions():
    with open(TRIVIA_FILE, "r") as f:
        questions = []
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 3:
                questions.append({
                    "question": parts[0],
                    "options": parts[1].split(","),
                    "answer": parts[2]
                })
        return questions

class TriviaView(View):
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(seconds=60)
        self.answer_buttons = []
        self.answered = False

        # Create buttons for each answer option
        for i, option in enumerate(question["options"]):
            button = Button(
                label=f"{chr(65 + i)}: {option}",
                style=discord.ButtonStyle.primary,
                custom_id=f"answer_{i}"
            )
            button.callback = self.check_answer
            self.answer_buttons.append(button)
            self.add_item(button)

    async def check_answer(self, interaction: discord.Interaction):
        if self.answered:
            return

        # Mark the question as answered
        self.answered = True

        # Get the selected answer from the button's custom_id
        selected_index = int(interaction.data['custom_id'].split('_')[1])
        selected_option = self.question["options"][selected_index]

        # Determine if the selected answer is correct
        is_correct = selected_option == self.question["answer"]

        # Disable all buttons
        for button in self.answer_buttons:
            button.disabled = True

        # Create the result embed
        description = f"Your answer: **{selected_option}**\n"
        if is_correct:
            description += "Correct! 🎉"
        else:
            description += f"Wrong! The correct answer was **{self.question['answer']}**."

        embed = discord.Embed(
            title="Trivia Time!",
            description=description,
            color=discord.Color.green() if is_correct else discord.Color.red()
        )

        await interaction.response.edit_message(embed=embed, view=self)

@client.command()
async def trivia(ctx):
    """Simple trivia game with a 60-second countdown and buttons."""
    questions = load_trivia_questions()
    question = random.choice(questions)
    view = TriviaView(question)

    # Countdown animation using deque
    countdown_frames = deque(["🟩" * i + "🟥" * (10 - i) for i in range(10, -1, -1)])

    embed = discord.Embed(
        title="Trivia Time!",
        description=f"{question['question']}\n\nYou have 60 seconds to answer!",
        color=0x973DA4
    )
    embed.set_footer(text="Choose an answer by pressing a button below!")

    # Send the trivia question with the buttons
    message = await ctx.send(embed=embed, view=view)

    # Countdown logic
    while datetime.now() < view.end_time:
        if view.answered:
            return  # Exit the loop if the question is answered

        time_left = (view.end_time - datetime.now()).seconds
        current_frame = countdown_frames[time_left // 6]  # Adjust frame per second

        embed.description = (
            f"{question['question']}\n\nTime Remaining: {time_left}s\n{current_frame}"
        )
        await message.edit(embed=embed)
        await asyncio.sleep(1)

    # If time runs out, disable the buttons and reveal the answer
    for button in view.answer_buttons:
        button.disabled = True

    embed.description = (
        f"Time's up! The correct answer was **{question['answer']}**."
    )
    await message.edit(embed=embed, view=view)


@client.command()
async def guess(ctx):
    """Guess the number game with lifelines and countdown timer."""
    number = random.randint(1, 100)
    lifelines = 5
    countdown_time = 120  # Countdown time in seconds
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=countdown_time)
    hearts = "❤" * lifelines  # Unicode heart character

    def loading_bar(lifelines_left):
        total_bars = 10
        filled = total_bars * lifelines_left // 5
        empty = total_bars - filled
        return f"[{'|' * filled}{' ' * empty}]"

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    embed = discord.Embed(
        title="Guess the Number",
        description=(
            "I've picked a number between 1 and 100. Start guessing!\n\n"
            f"Lifelines: {hearts}\n"
            f"Time Remaining: {str(end_time - datetime.now()).split('.')[0]}\n"
            f"Progress: {loading_bar(lifelines)}"
        ),
        color=discord.Color(0x973DA4),
    )
    game_message = await ctx.send(embed=embed)

    while lifelines > 0:
        try:
            # Calculate dynamic timeout
            time_left = (end_time - datetime.now()).total_seconds()
            if time_left <= 0:
                break

            # Edit the embed with updated time and lifelines
            embed.description = (
                f"Lifelines: {hearts}\n"
                f"Time Remaining: {str(timedelta(seconds=int(time_left))).split('.')[0]}\n"
                f"Progress: {loading_bar(lifelines)}"
            )
            await game_message.edit(embed=embed)

            # Wait for user input with dynamic timeout
            msg = await client.wait_for("message", check=check, timeout=min(5.0, time_left))
            guess = int(msg.content)

            if guess < number:
                response = "Too low! Try again."
            elif guess > number:
                response = "Too high! Try again."
            else:
                await ctx.send(embed=discord.Embed(
                    description=f"Congratulations! You guessed it! The number was {number}.",
                    color=discord.Color(0x973DA4)
                ))
                return

            lifelines -= 1
            hearts = "❤" * lifelines
            embed.description = (
                f"{response}\n\n"
                f"Lifelines: {hearts}\n"
                f"Time Remaining: {str(timedelta(seconds=int(time_left))).split('.')[0]}\n"
                f"Progress: {loading_bar(lifelines)}"
            )
            await game_message.edit(embed=embed)

        except asyncio.TimeoutError:
            lifelines -= 1
            hearts = "❤" * lifelines
            embed.description = (
                f"You took too long to respond!\n\n"
                f"Lifelines: {hearts}\n"
                f"Time Remaining: {str(timedelta(seconds=int(time_left))).split('.')[0]}\n"
                f"Progress: {loading_bar(lifelines)}"
            )
            await game_message.edit(embed=embed)

    # Game over scenarios
    if lifelines == 0:
        await ctx.send(embed=discord.Embed(
            description=f"You're out of lifelines! The number was {number}.",
            color=discord.Color(0x973DA4)
        ))
    else:
        await ctx.send(embed=discord.Embed(
            description=f"Time's up! The number was {number}.",
            color=discord.Color(0x973DA4)
        ))

class RPSView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)  # View persists until it is manually removed or the interaction is complete
        self.ctx = ctx
        self.choices = ["rock", "paper", "scissors"]
        self.user_choice = None

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.primary, emoji="🪨")
    async def rock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """User chooses Rock."""
        self.user_choice = "rock"
        await self.handle_choice(interaction, button)

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.primary, emoji="📄")
    async def paper_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """User chooses Paper."""
        self.user_choice = "paper"
        await self.handle_choice(interaction, button)

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.primary, emoji="✂️")
    async def scissors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """User chooses Scissors."""
        self.user_choice = "scissors"
        await self.handle_choice(interaction, button)

    async def handle_choice(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handles the choice made by the user."""
        if self.user_choice is None:
            return

        # Bot's choice
        bot_choice = random.choice(self.choices)

        # Determine the result
        if self.user_choice == bot_choice:
            result = "It's a tie!"
        elif (self.user_choice == "rock" and bot_choice == "scissors") or \
             (self.user_choice == "paper" and bot_choice == "rock") or \
             (self.user_choice == "scissors" and bot_choice == "paper"):
            result = "You win!"
        else:
            result = "You lose!"

        # Create the result embed
        result_embed = discord.Embed(
            title="Rock, Paper, Scissors - Result",
            description=f"Your choice: **{self.user_choice}**\nBot's choice: **{bot_choice}**\n**{result}**",
            color=discord.Color(0x973DA4)
        )

        # Disable all buttons
        for button in self.children:
            button.disabled = True

        # Send the result embed and edit the original message
        await interaction.message.edit(embed=result_embed, view=self)

# Command to start the game
@client.command()
async def rps(ctx):
    """Play Rock, Paper, Scissors with the bot."""
    # Create an embed to explain the game
    embed = discord.Embed(
        title="Rock, Paper, Scissors",
        description="Choose one of the options below: Rock, Paper, or Scissors.",
        color=discord.Color(0x973DA4)
    )

    # Create the view with buttons
    view = RPSView(ctx)
    await ctx.send(embed=embed, view=view)

@client.command()
async def scramble(ctx):
    """Word scramble game with lifelines, countdown, and an updated embed."""
    words = ["python", "discord", "bot", "developer", "gaming"]
    word = random.choice(words)
    scrambled = "".join(random.sample(word, len(word)))

    lifelines = 5
    countdown = 120  # 2 minutes
    loading_bar_length = 10

    # Initial embed
    embed = discord.Embed(
        title="Word Scramble",
        description=(
            f"Unscramble this word: **{scrambled}**\n\n"
            f"❤️ Lifelines: {lifelines} | ⏳ Time Remaining: {countdown} seconds\n"
            f"Progress: [{'█' * loading_bar_length}{' ' * (10 - loading_bar_length)}]"
        ),
        color=discord.Color(0x973DA4)
    )
    message = await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    while lifelines > 0 and countdown > 0:
        try:
            # Wait for the user's response
            msg = await client.wait_for("message", check=check, timeout=10.0)
            countdown -= 10

            if msg.content.lower() == word:
                embed.description = "🎉 Correct! You solved the word!"
                await message.edit(embed=embed)
                return
            else:
                lifelines -= 1
                loading_bar_length = max(0, lifelines * 2)
                embed.description = (
                    f"❌ Wrong! Try again.\n\n"
                    f"Unscramble this word: **{scrambled}**\n"
                    f"❤️ Lifelines: {lifelines} | ⏳ Time Remaining: {countdown} seconds\n"
                    f"Progress: [{'█' * loading_bar_length}{' ' * (10 - loading_bar_length)}]"
                )
                await message.edit(embed=embed)

        except asyncio.TimeoutError:
            countdown -= 10
            if countdown <= 0:
                break

            embed.description = (
                f"⏳ Time is ticking!\n\n"
                f"Unscramble this word: **{scrambled}**\n"
                f"❤️ Lifelines: {lifelines} | ⏳ Time Remaining: {countdown} seconds\n"
                f"Progress: [{'█' * loading_bar_length}{' ' * (10 - loading_bar_length)}]"
            )
            await message.edit(embed=embed)

    # End of game conditions
    if lifelines == 0 or countdown <= 0:
        embed.description = f"💔 Game Over! The correct word was **{word}**."
        await message.edit(embed=embed)


# 5. Would You Rather
@client.command()
async def wyr(ctx):
    """Would You Rather game."""
    questions = [
        "Would you rather have the ability to fly or be invisible?",
        "Would you rather be super rich or super smart?",
        "Would you rather live in space or under the sea?",
        "Would you rather always be too hot or too cold?",
        "Would you rather have no internet or no friends?",
        "Would you rather never sleep again but be fully rested or never eat again but be fully nourished?",
        "Would you rather time travel to the past or the future?",
        "Would you rather have a rewind button or a pause button for your life?",
        "Would you rather be able to talk to animals or speak all human languages?",
        "Would you rather have infinite knowledge or infinite wealth?",
        "Would you rather always be 10 minutes late or always 20 minutes early?",
        "Would you rather have a photographic memory or be able to forget anything you want?",
        "Would you rather explore the deepest parts of the ocean or the farthest reaches of space?",
        "Would you rather have unlimited energy or need only 1 hour of sleep?",
        "Would you rather live in a world with no crime or a world with no poverty?",
        "Would you rather have the power to heal others or the power to grant wishes?",
        "Would you rather know how the world began or how it will end?",
        "Would you rather relive your best day ever or know your future for the next 10 years?",
        "Would you rather be able to read minds or control minds?",
        "Would you rather never feel pain or never feel fear?"
    ]
    
    question = random.choice(questions)
    embed = discord.Embed(
        title="Would You Rather?",
        description=question,
        color=0x973DA4,
    )
    
    view = View()
    button1 = Button(label="Yes", style=discord.ButtonStyle.green)
    button2 = Button(label="No", style=discord.ButtonStyle.red)
    
    async def button_callback(interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("Only the user who used the command can respond!", ephemeral=True)
            return
    
        # Disable buttons after first interaction
        button1.disabled = True
        button2.disabled = True
        view.clear_items()
        view.add_item(button1)
        view.add_item(button2)
    
        await interaction.response.edit_message(view=view)
    
    button1.callback = button_callback
    button2.callback = button_callback
    
    view.add_item(button1)
    view.add_item(button2)
    
    await ctx.send(embed=embed, view=view)

@client.command(name="compare")
async def compare(ctx, *, dreams: str = None):
    """Compare two dreams and highlight their similarities."""
    if not dreams or " and " not in dreams:
        # Send an error message if the dreams are not properly provided
        await ctx.send(embed=discord.Embed(
            description=(
                "_⚠️ **Error**: Please provide two dreams separated by 'and'._\n"
                "_Example usage: `!compare dream1_description and dream2_description`_"
            ),
            color=0x973DA4
        ))
        return

    # Split the input into two dreams based on the "and" separator
    dream1, dream2 = map(str.strip, dreams.split(" and ", 1))

    if not dream1 or not dream2:
        # Send an error message if one of the dreams is missing after splitting
        await ctx.send(embed=discord.Embed(
            description=(
                "_⚠️ **Error**: Please ensure both dreams are properly described._\n"
                "_Example usage: `!compare dream1_description and dream2_description`_"
            ),
            color=0x973DA4
        ))
        return

    # List of possible similarities
    similarities = [
        "Both involve a sense of exploration.",
        "Recurring themes of fear or excitement.",
        "A focus on personal transformation.",
        "An underlying sense of mystery.",
        "Dreams reflect your current emotions.",
        "They both symbolize unresolved desires.",
        "Recurring motifs of struggle or success.",
        "A connection to past experiences.",
        "Both showcase heightened creativity and imagination.",
        "Dreams highlight suppressed fears or anxieties.",
        "They share surreal or otherworldly elements.",
        "A reflection of inner conflicts and dilemmas.",
        "Both convey messages through symbolic imagery.",
        "Dreams can reveal your subconscious aspirations.",
        "They hint at changes happening in your life.",
        "Both might involve interactions with unfamiliar faces.",
        "Dreams often explore alternative versions of reality.",
        "A sense of déjà vu or familiarity connects them.",
        "Both may involve navigating challenging environments.",
        "They can act as a bridge between memory and emotion."
    ]

    # Choose a random similarity
    result = random.choice(similarities)

    # Create an embed to display the comparison
    embed = discord.Embed(
        title="Dream Comparison",
        description="Highlighting the similarities between your dreams",
        color=0x973DA4
    )

    # Add fields for each dream
    embed.add_field(name="Dream 1", value=dream1[:1024], inline=False)
    embed.add_field(name="Dream 2", value=dream2[:1024], inline=False)

    # Add the similarity result
    embed.add_field(name="Similarities", value=result, inline=False)

    # Send the embed
    await ctx.send(embed=embed)


# Command 8: Dream Prediction
@client.command(name="predict")
async def predict(ctx):
    """Provide a creative dream prediction."""
    predictions = [
        "You might soar through the skies, touching the stars.",
        "A loved one from your past could visit you with a message.",
        "A mysterious door could open, revealing a hidden world.",
        "You might find yourself breathing underwater, exploring a sunken city.",
        "A talking animal might guide you on an unexpected adventure.",
        "A futuristic cityscape might stretch before your eyes.",
        "You could relive a cherished childhood memory with a twist.",
        "A surreal and colorful landscape might unfold, defying logic.",
        "You might experience the sensation of losing something precious, only to rediscover it.",
        "A hidden room in your home could reveal forgotten secrets.",
        "You might walk through a forest where the trees whisper your name.",
        "A celestial being could appear, offering you profound wisdom.",
        "You might find yourself on a distant planet, meeting its inhabitants.",
        "A mirror might show you an alternate version of yourself.",
        "You could witness a breathtaking meteor shower that feels deeply personal.",
        "An ancient book might hold the answers to questions you've never asked.",
        "You might dance in a field of flowers that glow under a moonlit sky.",
        "A forgotten melody might play, guiding you to a place of peace.",
        "You could find yourself painting a masterpiece that comes to life.",
        "A labyrinth might test your courage and intuition.",
        "You might dream of walking on clouds, feeling weightless and free.",
        "A stranger might offer you a choice that changes everything.",
        "You could find yourself at the edge of a cliff, overlooking infinite possibilities.",
        "An old friend might join you on a journey through time.",
        "You might discover a treasure chest filled with memories.",
        "A garden of talking flowers could share their secrets with you.",
        "You might traverse a glowing bridge connecting two worlds.",
        "An eclipse might fill the sky, revealing hidden truths.",
        "You could find yourself at a grand feast, where every dish tells a story.",
        "A train ride through a dreamlike landscape might await you.",
        "You might encounter a guardian who tests your resolve.",
        "An enchanted forest might reveal its magical inhabitants.",
        "You could dream of being a hero in a storybook tale.",
        "A shimmering portal might beckon you to step through.",
        "You might find yourself conversing with the moon.",
        "A storm could rage around you, yet you feel completely calm.",
        "You could follow a trail of glowing footprints to an unknown destination.",
        "A library of infinite knowledge might appear before you.",
        "You might dream of unlocking a puzzle that holds great significance.",
        "A phoenix might rise before you, symbolizing renewal.",
        "You could find yourself as the conductor of a cosmic orchestra.",
        "A castle in the clouds might be your next destination.",
        "You might meet your future self in a moment of clarity.",
        "A golden path might lead you to your heart's desire.",
        "You could witness a dance of fireflies illuminating the night.",
        "A whispering wind might guide you to a place of wonder.",
        "You might dream of being part of a celestial festival.",
        "A glowing compass could point you toward your destiny."
    ]

    prediction = random.choice(predictions)

    # Create an embed for the dream prediction
    embed = discord.Embed(
        title="✨ Dream Prediction ✨",
        description=prediction,
        color=0x973DA4
    )
    embed.set_footer(text="Let your imagination soar into the realm of dreams!")

    # Send the embed
    await ctx.send(embed=embed)


@client.command(name="poll")
async def poll(ctx, *, dream_description: str = None):
    """Create a community poll to vote on a dream's meaning."""
    if not dream_description:
        await ctx.send(embed=discord.Embed(
            description="_⚠️ **Error**: Please provide a dream description to create a poll._\n_Example usage: `!poll dream_description`_",
            color=0x973DA4
        ))
        return

    embed = discord.Embed(
        title="Community Dream Poll",
        description=f"Dream: {dream_description}\n\nWhat do you think this dream means?",
        color=0x973DA4,
    )

    countdown_embed = embed.copy()
    countdown_embed.add_field(name="⏳ Time Remaining", value="60 seconds", inline=False)

    view = View()
    button_labels = [
        "Freedom", "Fear", "The Unknown", "Adventure", "Transformation",
        "Love", "Regret", "Growth", "Happiness", "Loss"
    ]

    votes = Counter()
    voters = set()

    # Dynamically add buttons
    for label in button_labels:
        button = Button(label=label, style=discord.ButtonStyle.primary)

        async def button_callback(interaction, label=label):
            if interaction.user.id in voters:
                await interaction.response.send_message(
                    "You have already voted!", ephemeral=True
                )
                return

            voters.add(interaction.user.id)
            votes[label] += 1
            await interaction.response.send_message(
                f"Thanks for voting: {label}", ephemeral=True
            )

        button.callback = button_callback
        view.add_item(button)

    # Send the initial embed and view
    message = await ctx.send(embed=countdown_embed, view=view)

    # Countdown logic
    for remaining in range(59, 0, -1):
        countdown_embed.set_field_at(0, name="⏳ Time Remaining", value=f"{remaining} seconds", inline=False)
        await message.edit(embed=countdown_embed)
        await asyncio.sleep(1)

    # Disable buttons
    for item in view.children:
        item.disabled = True

    # Create the results display
    total_votes = sum(votes.values())
    results = []

    for label in button_labels:
        count = votes[label]
        percentage = (count / total_votes * 100) if total_votes > 0 else 0
        bar = "█" * int(percentage // 10) + "░" * (10 - int(percentage // 10))
        results.append(f"**{label}**: {count} votes ({percentage:.1f}%)\n`[{bar}]`")

    results_description = "\n\n".join(results) if results else "No votes received."

    results_embed = discord.Embed(
        title="Poll Results",
        description=f"Dream: {dream_description}\n\n{results_description}",
        color=0x973DA4
    )

    # Edit the original message to display results
    await message.edit(embed=results_embed, view=view)

# Command 11: Dream Archetype Quiz
@client.command(name="quiz")
async def quiz(ctx):
    # Generate a random question
    questions = [
        "What best describes your usual dreams?",
        "What kind of themes are most common in your dreams?",
        "How would you describe the mood of your dreams?",
        "What do your dreams usually revolve around?",
        "What stands out most in your dreams?",
    ]
    question = random.choice(questions)

    # Archetypes and their specific responses
    archetypes = {
        "Adventurous": "exploration, daring journeys, and excitement.",
        "Reflective": "self-discovery, introspection, and thoughtful insights.",
        "Problem-Solver": "creative solutions, overcoming challenges, and clever ideas.",
        "Creative": "artistic expression, imaginative landscapes, and inspiration.",
        "Philosophical": "deep thoughts, big questions, and meaningful ideas.",
        "Challenging": "difficult obstacles, growth through struggle, and resilience.",
        "Peaceful": "tranquility, harmony, and serene experiences.",
        "Confusing": "abstract scenarios, unpredictable twists, and mystery.",
        "Motivational": "encouraging visions, personal drive, and positive energy.",
        "Visionary": "future-focused ideas, innovation, and groundbreaking concepts."
    }

    # Embed setup
    embed = Embed(
        title="Dream Archetype Quiz",
        description=f"Answer the question: {question}",
        color=0x973DA4,
    )

    view = View()

    async def disable_buttons(interaction: Interaction):
        """Disables all buttons after a user interacts."""
        for item in view.children:
            item.disabled = True
        await interaction.message.edit(view=view)

    for archetype, response in archetypes.items():
        button = Button(label=archetype, style=ButtonStyle.secondary)

        async def button_callback(interaction: Interaction, archetype=archetype, response=response):
            await interaction.response.send_message(
                f"You are a **{archetype} Dreamer**! Your dreams often reflect {response}",
                ephemeral=True
            )
            await disable_buttons(interaction)

        button.callback = button_callback
        view.add_item(button)

    await ctx.send(embed=embed, view=view)


# Command 12: Astral Projection Guide
@client.command(name="astral")
async def astral(ctx):
    steps = [
        "Relax and focus on your breathing.",
        "Visualize yourself leaving your body.",
        "Imagine a silver cord connecting you to your physical form.",
        "Explore your surroundings mentally.",
        "Try to remain calm and aware during the experience.",
        "If you feel scared, focus on returning to your body.",
        "Practice meditation to improve focus.",
        "Use binaural beats to aid relaxation.",
        "Keep a journal to track your progress.",
        "Read about others' experiences for inspiration."
    ]
    embed = discord.Embed(
        title="Astral Projection Guide",
        description="Follow these steps to attempt astral projection safely:\n\n" +
                    "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)]),
        color=0x973DA4,
    )

    view = View()
    button = Button(label="Learn More", style=discord.ButtonStyle.link, url="https://example.com/astral-projection-guide")
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

@client.command()
async def owner(ctx):
    your_user_id = 1326848930465452032  # Replace this with your Discord user ID
    user = client.get_user(your_user_id)
    message = "Owner: Jojo_07_03\nSent a Direct message for any queries or if you would like to purchase premium for your preferred time frame."
    embed = discord.Embed(description = message, color = 0x973DA4)
    embed.set_footer(
        text="Bot by jojo_07_03 | Made with ❤️",
        icon_url=user.avatar.url if user and user.avatar else None,
    )
    embed.add_field(name = "Use", value = "Use the `d!buy_premium` command to buy the premium version of the bot.")
    await ctx.send(embed=embed)

@client.command(name="help")
async def help_command(ctx):
    """Displays a funky help menu."""
    your_user_id = 1326848930465452032  # Replace this with your Discord user ID
    user = client.get_user(your_user_id)
    embed = discord.Embed(
        title="✨ Welcome to the Help Menu! ✨",
        description="Here are the commands that you can use with this bot. 🚀\n\nType the commands with the prefix `d!` to get started!",
        color=0x973DA4,  # Funky orange color
    )

    embed.add_field(
        name="🌟 **Main Commands** 🌟",
        value=(
            "`dream` - Get an information for your dreams\n"
            "`poll` - Poll the dream and enjoy the responses\n"
            "`astral` - Get the astral predictions from the bot\n"
            "`compare` - Compare your two dreams\n"
            "`predict` - Bot will Predict your next dream\n"
            "`quiz` - Take a quiz to find your dream archetype\n"
        ),
        inline=False,
    )
    embed.add_field(
        name="🎲 **Fun Commands** 🎲",
        value=(
            "`wyr` - Play 'Would You Rather?'.\n"
            "`scramble` - Guess the scrambled word\n"
            "`trivia` - Guess the correct answer to a trivia aquestion\n"
            "`rps` - Play Rock, Paper, Scissors with the bot\n"
            "`guess` - Guess a number between 1 and 100\n"
        ),
        inline=False,
    )
    embed.add_field(
        name="👑 **Premium Commands** 👑",
        value=(
            "`journal` - Create a journal of your dreams in bot\n"
            "`view_journal` - Check all of your entries of journal and others\n"
            "`clear_entry` - Clear a specific entry from the journal\n"
            "`Clear_journal` - Remove all entries from your journal\n"
            "`dreams` - View detailed analysis of your dreams\n"
            "`buy_premium` - Buy the premium\n"
        ),
        inline=False,
    )
    embed.add_field(
        name="🔥 **Misc. Commands** 🔥",
        value=(
            "`pay_respect` - Pay respect to the bot's owner\n"
            "`suggest` - Suggest the changes that you want in the bot\n"
            "`owner` - Check the owner of the bot\n"
        ),
        inline=False,
        
    )
    embed.add_field(
        name="🔗 **Other links**",
        value="[Top.gg]() | [My Server](https://discord.gg/tdjTpSQa) | [Add Me](https://discord.com/oauth2/authorize?client_id=1326850307619295245&permissions=564464400067824&response_type=code&redirect_uri=https%3A%2F%2Fdiscord.com%2Foauth2%2Fauthorize%3Fclient_id%3D1326850307619295245&integration_type=0&scope=guilds.join+guilds.members.read+bot+guilds+guilds.channels.read)",
        inline=False,
    )
    embed.set_footer(
        text="Bot by jojo_07_03 | Made with ❤️",
        icon_url=user.avatar.url if user and user.avatar else None,
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1328305112220700692/1328369358375751751/standard.gif?ex=678673de&is=6785225e&hm=319ca6586824bd049d7d2821ce7f8b7f940e10b66526e46219356ef5a46c7fb1&=&width=750&height=300")
    
    await ctx.send(embed=embed)

@client.command()
async def buy_premium(ctx):
    embed = discord.Embed(
        title="Buy Premium",
        description=(
            "_If you want to buy the premium version of the bot._\n"
            "> **Please message the owner**\n\n"
            "> **jojo_07_03**"
        ),
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1328305112220700692/1328305165870043166/WhatsApp_Image_2025-01-13_at_2.07.16_AM.jpeg?ex=67878996&is=67863816&hm=271710db4e433af654926cbffb00c5342ac8b11153db4ee0e7247bc383c4b3fe&=&format=webp&width=630&height=630")
    embed.set_footer(text="Made by jojo_07_03 | Made with ❤️")
    # Send the embed with buttons
    await ctx.send(embed=embed)



if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv('DISCORD_BOT_TOKEN'))