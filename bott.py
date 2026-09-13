import os
import discord
from discord import app_commands
from discord.ext import commands

# ============ AYARLAR ============
TOKEN = os.getenv("TOKEN")              # ← GitHub'da görünmez
ADMIN_ID = 1518482876566605877
GUILD_ID = 1532403639115845742
# =================================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ---------- MODAL ----------
class IhbarModal(discord.ui.Modal, title="İhbar Formu"):
    adres = discord.ui.TextInput(
        label="Adres",
        style=discord.TextStyle.paragraph,
        placeholder="İhbar atmak istediğiniz adresi yazın...",
        required=True,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user

        await interaction.response.send_message(
            "✅ **İhbarınız alındı.**\n\n"
            "📌 **Yapmak için 20 videonun altına `/Asayisube yaz g!r` yazınız.**\n\n"
            "⏳ Attığınız adrese ihbar gönderilecektir **1 saat içerisinde**.",
            ephemeral=True,
        )

        try:
            admin = await bot.fetch_user(ADMIN_ID)
            embed = discord.Embed(title="🚨 YENİ İHBAR GELDİ", color=0xFF0000)
            embed.add_field(
                name="👤 Gönderen",
                value=f"{user.mention} (`{user.name}` • `{user.id}`)",
                inline=False,
            )
            embed.add_field(name="📍 Adres", value=self.adres.value, inline=False)
            embed.set_footer(text="Onayla veya Reddet")
            embed.timestamp = discord.utils.utcnow()

            view = OnayView(target_user_id=user.id)
            await admin.send(embed=embed, view=view)
        except Exception as e:
            print(f"[HATA] Admin DM gönderilemedi: {e}")


# ---------- ONAY / RED ----------
class OnayView(discord.ui.View):
    def __init__(self, target_user_id: int):
        super().__init__(timeout=None)
        self.target_user_id = target_user_id

    @discord.ui.button(label="Onayla", emoji="✅", style=discord.ButtonStyle.success)
    async def onayla(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != ADMIN_ID:
            await interaction.response.send_message(
                "❌ Bu butonu kullanma yetkin yok.", ephemeral=True
            )
            return

        try:
            target = await bot.fetch_user(self.target_user_id)
            dm_embed = discord.Embed(
                title="✅ İHBAR GÖNDERİLMİŞTİR",
                description="İhbar gönderilmiştir adresinize.\n\n**Gönderen kişi:** @doedaxq",
                color=0x00FF00,
            )
            dm_embed.timestamp = discord.utils.utcnow()
            await target.send(embed=dm_embed)
        except Exception as e:
            print(f"[HATA] Kullanıcıya DM gönderilemedi: {e}")

        old_embed = interaction.message.embeds[0]
        new_embed = discord.Embed(title="✅ İHBAR ONAYLANDI", color=0x00FF00)
        for field in old_embed.fields:
            new_embed.add_field(name=field.name, value=field.value, inline=field.inline)
        new_embed.set_footer(text=f"Onaylayan: {interaction.user.name}")
        new_embed.timestamp = discord.utils.utcnow()

        await interaction.response.edit_message(embed=new_embed, view=None)

    @discord.ui.button(label="Reddet", emoji="❌", style=discord.ButtonStyle.danger)
    async def reddet(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != ADMIN_ID:
            await interaction.response.send_message(
                "❌ Bu butonu kullanma yetkin yok.", ephemeral=True
            )
            return

        try:
            target = await bot.fetch_user(self.target_user_id)
            dm_embed = discord.Embed(
                title="❌ İHBAR REDDEDİLDİ",
                description="İhbarınız yetkili tarafından reddedildi.",
                color=0xFF0000,
            )
            await target.send(embed=dm_embed)
        except Exception as e:
            print(f"[HATA] Kullanıcıya DM gönderilemedi: {e}")

        old_embed = interaction.message.embeds[0]
        new_embed = discord.Embed(title="❌ İHBAR REDDEDİLDİ", color=0x808080)
        for field in old_embed.fields:
            new_embed.add_field(name=field.name, value=field.value, inline=field.inline)
        new_embed.set_footer(text=f"Reddeden: {interaction.user.name}")
        new_embed.timestamp = discord.utils.utcnow()

        await interaction.response.edit_message(embed=new_embed, view=None)


# ---------- PANEL BUTONU ----------
class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="İhbar Bas",
        emoji="🚨",
        style=discord.ButtonStyle.danger,
        custom_id="ihbar_bas_btn",
    )
    async def ihbar_bas(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IhbarModal())


# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"✅ Bot hazır: {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ {len(synced)} slash komut yüklendi")
    except Exception as e:
        print(f"[HATA] Komut yükleme: {e}")

    bot.add_view(PanelView())


# ---------- SLASH KOMUT ----------
@bot.tree.command(name="asayisube", description="İhbar panelini gönderir")
async def asayisube(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🚨 /ASAYİSUBE İHBAR BOTU",
        description=(
            "**MERHABA /ASAYİSUBE İHBAR BOTUMA HOŞGELDİNİZ**\n\n"
            "İHBAR ATMAK İÇİN AŞAĞIDAKİ **İHBAR BUTONU** TIKLAYINIZ"
        ),
        color=0x2B2D31,
    )
    embed.set_footer(text="/Asayisube • İhbar Sistemi")
    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message(embed=embed, view=PanelView())


# ---------- ÇALIŞTIR ----------
if __name__ == "__main__":
    bot.run(TOKEN)
