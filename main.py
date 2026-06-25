import os
import random
import string
import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta

# ========================================================
# CONFIGURAZIONE ID
# ========================================================
ID_CANALE_RECENSIONI = 1519310548024426577  # Canale dove mandare le recensioni
ID_CANALE_LOG_FINE = 1519403485852991781    # Canale per il log segreto di fine corsa

# Target fisso per la menzione nel widget aggiornato a ky7n
TARGET_MENTION = "@ky7n"

# ========================================================
# DATABASE VARIABILI TIER & PAROLE CHIAVE MINIMALI
# ========================================================
TIERS = [
    {"name": "BASIC TWEAK", "price": "5€", "ansi_color": "[1;32m"},     # Verde
    {"name": "ADVANCED TWEAKS", "price": "10€", "ansi_color": "[1;36m"}, # Azzurro
    {"name": "ULTRA TWEAKS", "price": "25€", "ansi_color": "[1;35m"},    # Viola
    {"name": "ELITE TWEAKS", "price": "45€", "ansi_color": "[1;31m"}     # Rosso
]

# Varianti corte per generare tantissimi feedback minimali diversi
TAGS_PRESTAZIONI = [
    "+fps -input lag",
    "+smoothness -delay",
    "max fps +vouch",
    "-latency +fps fr",
    "zero delay +fps boost",
    "+performance -stutter",
    "input lag fixed",
    "0 delay fr fr",
    "+fps -latency optimized",
    "max performance +smoothness"
]

BANNER_URL = 'https://cdn.discordapp.com/attachments/1515438245813551147/1518560640778633246/ce2828a1-7b03-46bb-b7d3-710697e0ae07.png?ex=6a3a5d4e&is=6a390bce&hm=f14e25633beb62c6c1f6c81a4102619dff3c71973a73f30edd4c0f34b5f85a43&'

class BotRecensioniInvisibili(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        
        self.combinazioni_rimanenti = []
        self.tempo_attesa_minuti = 109  # 1 ora e 49 minuti
        self.prossimo_invio = None

    def genera_tutte_le_combinazioni(self):
        lista_totale = []
        # Genera tantissime combinazioni corte incrociando i Tier con i tag prestazionali scritti in modi diversi
        for tier in TIERS:
            for tag1 in TAGS_PRESTAZIONI:
                for tag2 in TAGS_PRESTAZIONI:
                    if tag1 != tag2:
                        testo_completo = f"+rep {TARGET_MENTION} x1 {tier['name'].lower()} {tier['price']} {tag1} {tag2} ⭐⭐⭐⭐⭐"
                        
                        lista_totale.append({
                            "text": testo_completo,
                            "tier_name": tier["name"],
                            "tier_price": tier["price"],
                            "ansi_color": tier["ansi_color"]
                        })
        random.shuffle(lista_totale)
        return lista_totale

    async def setup_hook(self):
        self.combinazioni_rimanenti = self.genera_tutte_le_combinazioni()
        await self.tree.sync()

    async def on_ready(self):
        print(f"🚀 Bot Pronto. Sistema Vouch minimali ad alto realismo integrato.")

bot = BotRecensioniInvisibili()

def genera_username_unico():
    """Genera un nome utente completamente casuale e dinamico per evitare ripetizioni strutturali"""
    stili = [
        f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}",
        f"client_{''.join(random.choices(string.digits, k=4))}{random.choice(['x', 'z', '_', 'ff'])}",
        f"{''.join(random.choices(string.ascii_lowercase, k=6))}_{random.randint(10, 99)}",
        f"mako_customer_{random.randint(100, 999)}"
    ]
    return random.choice(stili)

async def invia_singola_recensione():
    if not bot.combinazioni_rimanenti:
        canale_log = bot.get_channel(ID_CANALE_LOG_FINE)
        if canale_log:
            await canale_log.send(f"🛑 **[LOG]** Finito il pool di combinazioni. Arresto di sicurezza eseguito.")
        bot.prossimo_invio = None
        loop_recensioni_orologio.stop()
        return False

    canale_recensioni = bot.get_channel(ID_CANALE_RECENSIONI)
    if canale_recensioni:
        data_recensione = bot.combinazioni_rimanenti.pop(0)
        
        # Generazione del nome utente totalmente casuale ad ogni ciclo
        utente_fake = genera_username_unico()
        
        color_ansi = data_recensione["ansi_color"]
        tier_str = f"{data_recensione['tier_name']} ({data_recensione['tier_price']})"
        
        ansi_widget = (
            f"```ansi\n"
            f"[1;37m┌────────────────────────────────────────┐[0m\n"
            f"[1;35m 👤 CLIENT:[0m {utente_fake}\n"
            f"{color_ansi} 📦 SERVICE:[0m {tier_str}\n"
            f"[1;33m ⭐ RATING:[0m 5/5 ⭐ ⭐ ⭐ ⭐ ⭐\n"
            f"[1;37m└────────────────────────────────────────┘[0m\n"
            f"```\n"
            f"📝 **FEEDBACK RILASCIATO:**\n"
            f"> *{data_recensione['text']}*\n\n"
            f"📡 *🛒 [Acquisto Verificato via Sito Web] — Ottimizzazione registrata nel sistema MKO Network.*"
        )

        embed = discord.Embed(
            description=ansi_widget,
            color=discord.Color.from_str("#ffffff")
        )
        embed.set_author(
            name=f"{utente_fake} ha rilasciato un Vouch!",
            icon_url=bot.user.display_avatar.url
        )
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=f"MKO TWEAKS SYSTEM • USER ID: {random.randint(200000000000000000, 999999999999999999)}")
        embed.timestamp = datetime.now()

        await canale_recensioni.send(embed=embed)
        return True
    return False

# ========================================================
# TASK AD ALTA PRECISIONE (OGNI MINUTO)
# ========================================================
@tasks.loop(minutes=1)
async def loop_recensioni_orologio():
    if bot.prossimo_invio is None:
        return

    if datetime.now() >= bot.prossimo_invio:
        successo = await invia_singola_recensione()
        
        if successo:
            bot.tempo_attesa_minuti += 29
            bot.prossimo_invio = datetime.now() + timedelta(minutes=bot.tempo_attesa_minuti)
            print(f"[INFO] Recensione inviata con grafica ANSI. Prossima tra {bot.tempo_attesa_minuti} minuti.")

# ========================================================
# COMANDI SLASH PROTETTI (SOLO AMMINISTRATORI)
# ========================================================
@bot.tree.command(name="start_reviews", description="Avvia il sistema di recensioni segrete.")
@app_commands.default_permissions(administrator=True)
async def start_reviews(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    if loop_recensioni_orologio.is_running():
        await interaction.followup.send("ℹ️ Sistema già attivo.", ephemeral=True)
    else:
        bot.tempo_attesa_minuti = 109
        prima_inviata = await invia_singola_recensione()
        
        if prima_inviata:
            bot.prossimo_invio = datetime.now() + timedelta(minutes=bot.tempo_attesa_minuti)
            loop_recensioni_orologio.start()
            await interaction.followup.send("✅ Configurazione applicata. Sistema grafico ANSI avviato.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Errore nell'invio iniziale.", ephemeral=True)

@bot.tree.command(name="stop_reviews", description="Spegne il sistema di recensioni segrete.")
@app_commands.default_permissions(administrator=True)
async def stop_reviews(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if not loop_recensioni_orologio.is_running():
        await interaction.followup.send("ℹ️ Il sistema è già spento.", ephemeral=True)
    else:
        bot.prossimo_invio = None
        loop_recensioni_orologio.stop()
        await interaction.followup.send("🛑 Sistema arrestato con successo.", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRORE: DISCORD_TOKEN mancante.")
