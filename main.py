import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

SELLER_ROLE_ID = 1394722037200584814
WATCHED_CHANNELS = [1393973218322284665, 1393973411252011028, 1393972988482949271, 1393973484467650642, 1393973937666396181, 1393973711140552786]
WARNING_ROLES = [1089654113647730698, 1089654165938131005, 1089654215070208152]
ALERT_CHANNEL_ID = 1136065799208046603

robux_price = 2_000_000  # default: 2m per 1 robux
warnings_dict = {}

class SellerRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="الحصول على رتبة بائع", custom_id="get_seller", style=discord.ButtonStyle.success))

@bot.command()
@commands.has_permissions(administrator=True)
async def رتبه(ctx):
    embed = discord.Embed(title="للحصول على رتبة بائع اضغط على الزر بالأسفل")
    await ctx.send(embed=embed, view=SellerRoleView())

class EncryptModal(Modal, title="ادخل النص ليتم تشفيره"):
    input = TextInput(label="نص التشفير", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction):
        word_map = {
            "مطلوب": "مtلوب", "شراء": "شrاء", "بيع": "بي3", "سعر": "س3ر",
            "تشتري": "تشترY", "سوم": "سوm", "اسعار": "اسع4ر", "حسابات": "حس4بات",
            "ابيع": "ابyع", "متوفر": "متوFر"
        }
        result = self.input.value
        for k, v in word_map.items():
            result = result.replace(k, v)
        await interaction.response.send_message(f"النص المشفر:\n{result}", ephemeral=True)

class EncryptButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="تشفير", custom_id="encrypt_btn", style=discord.ButtonStyle.primary))

@bot.command()
async def تشفير(ctx):
    await ctx.send("اضغط على الزر لتشفير رسالة", view=EncryptButtonView())


@bot.command()
async def شوب(ctx):
    await ctx.send("تم فتح الشوب  الساعة 1 الظهر و سيتم غلقها 1 مساء \n @everyone")
    
@bot.event
async def on_interaction(interaction):
    custom_id = interaction.data.get("custom_id")
    if custom_id == "encrypt_btn":
        await interaction.response.send_modal(EncryptModal())
    elif custom_id == "get_seller":
        role = interaction.guild.get_role(SELLER_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("تم إعطاؤك رتبة بائع!", ephemeral=True)

@bot.event
async def on_message(message):
    if message.channel.id in WATCHED_CHANNELS and not message.author.bot:
        await message.channel.send("لتفادي النصب و الاحتيال يرجي استخدام <#1136065799208046603>")
    await bot.process_commands(message)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="مساعدة", description="الأوامر المتاحة:")
    embed.add_field(name="-رتبه", value="إرسال زر إعطاء رتبة بائع (للأدمن فقط)", inline=False)
    embed.add_field(name="-تشفير", value="زر لتشفير النصوص المرتبطة بالبيع والشراء", inline=False)
    embed.add_field(name="-tax <المبلغ>", value="حساب كم روبوكس تقدر تشتري بعد الضريبة", inline=False)
    embed.add_field(name="-setprice <السعر>", value="تغيير سعر الروبوكس (أدمن فقط)", inline=False)
    embed.add_field(name="-w @user", value="تحذير مستخدم حتى 3 مرات مع إزالة الرتب في النهاية", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def tax(ctx, amount: str):
    try:
        global robux_price
        if amount.endswith("m"):
            amount = int(amount[:-1]) * 1_000_000
        elif amount.endswith("k"):
            amount = int(amount[:-1]) * 1_000
        else:
            amount = int(amount)

        after_tax = int(amount / (1 + 0.052632))
        robux = after_tax // robux_price
        tax_total = int(amount - after_tax)
        middleman_total = int(amount * 0.025)
        total_all = tax_total + middleman_total

        embed = discord.Embed(title="حساب الضرائب")
        embed.add_field(name="الضريبة العادية", value=f"{tax_total} كريدت", inline=False)
        embed.add_field(name="ضريبة الوسيط (2.5%)", value=f"{middleman_total} كريدت", inline=False)
        embed.add_field(name="إجمالي الخصم", value=f"{total_all} كريدت", inline=False)
        embed.add_field(name="الروبوكس المتوقع", value=f"{robux} روبوكس", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"صيغة غير صحيحة. مثال: `-tax 2m`\n{e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setprice(ctx, price: int):
    global robux_price
    robux_price = price
    await ctx.send(f"تم تغيير السعر إلى 1 روبوكس = {robux_price} كريدت")

@bot.command()
async def w(ctx, member: discord.Member):
    guild = ctx.guild
    user_id = member.id
    count = warnings_dict.get(user_id, 0)
    
    if count >= 3:
        await ctx.send("هذا المستخدم وصل الحد الأقصى من التحذيرات.")
        return
    else:
        await ctx.send (f" تم إعطاء <@{user_id}> تحذير ")
        

    role = guild.get_role(WARNING_ROLES[count])
    await member.add_roles(role)
    warnings_dict[user_id] = count + 1

    if warnings_dict[user_id] == 3:
        await ctx.send(f"{member.mention} وصل للحد الأقصى من التحذيرات!")
        for role_id in WARNING_ROLES:
            role = guild.get_role(role_id)
            await member.remove_roles(role)
        seller_role = guild.get_role(SELLER_ROLE_ID)
        if seller_role:
            await member.remove_roles(seller_role)

@bot.event
async def on_ready():
    bot.add_view(SellerRoleView())
    bot.add_view(EncryptButtonView())
    print(f"✅ Bot is ready: {bot.user}")

# إبقاء البوت شغال دائمًا عبر port 8080
keep_alive()

# تشغيل البوت
TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
