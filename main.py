import os
import random
import discord
from discord.ext import commands, tasks
from datetime import datetime

# ========================================================
# CONFIGURAZIONE ID
# ========================================================
ID_CANALE_RECENSIONI = 1519310548024426577  # Canale dove mandare le recensioni
ID_CANALE_LOG_FINE = 1519403485852991781    # Canale per il log segreto di fine corsa

# Componenti per i nickname (stile reali utenti discord)
PREFISSI_USER = ["vortex", "zack", "hyper", "dark", "liquid", "gamer", "swift", "glitch", "alpha", "shadow", "neon", "apex", "ghost", "pulse"]
SUFISSI_USER = ["_fps", "99", "_tuning", "gg", "ovr", "x", "⚡", "_pc", "plays", "04", "_clutch", "god", "z", "xd", "_w", "fr", "hz"]

# Componenti per i testi (gergali, minuscoli, stile discord)
BLOCCO_1 = [
    "goat tweak fr",
    "fucking best optimization out there",
    "games feel so good now",
    "literally zero lag after this",
    "my pc was so bloated and slow before",
    "input delay is completely gone fr",
    "holy shit my fps just doubled"
]

BLOCCO_2 = [
    "less process in my life and more fps",
    "goat os config setup is insane",
    "advanced pack went hard as fuck",
    "mako really fixed my shitty delayed inputs",
    "the bios tuning is actual magic",
    "windows feels smooth like butter now",
    "best money i ever spent on my setup no cap"
]

BLOCCO_3 = [
    "big vouch for mako",
    "w tweak fr go buy it",
    "10/10 worth every penny",
    "actual massive w",
    "highly recommend if u wanna win matches",
    "legit crazy difference fr fr",
    "stutters are completely gone goodbye"
]

class BotRecensioniInvisibili(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        
        self.combinazioni_rimanenti = []
        self.tempo_corrente_minuti = 109  # Parte da 1 ora e 49 minuti

    def genera_tutte_le_combinazioni(self):
        lista_totale = []
        for b1 in BLOCCO_1:
            for b2 in BLOCCO_2:
                for b3 in BLOCCO_3:
                    testo_recensione = f'"{b1}, {b2}. {b3} ⭐⭐⭐⭐⭐"'
                    lista_totale.append(testo_recensione)
        random.shuffle(lista_totale)
        return lista_totale

    async def setup_hook(self):
        self.combinazioni_rimanenti = self.genera_tutte_le_combinazioni()
        await self.tree.sync()

    async def on_ready(self):
        print(f"🚀 Bot Pronto. Sistema anti-sgamo attivo.")

bot = BotRecensioniInvisibili()

# ========================================================
# TASK DINAMICO CON INCREMENTO DEL TEMPO
# ========================================================
@tasks.loop(minutes=109)
async def loop_recensioni_dinamico():
    if not bot.combinazioni_rimanenti:
        canale_log = bot.get_channel(ID_CANALE_LOG_FINE)
        if canale_log:
            await canale_log.send(f"🛑 **[LOG]** Finito il pool di combinazioni. Arresto di sicurezza eseguito.")
        loop_recensioni_dinamico.stop()
        return

    canale_recensioni = bot.get_channel(ID_CANALE_RECENSIONI)
    if canale_recensioni:
        recensione = bot.combinazioni_rimanenti.pop(0)
        utente = f"{random.choice(PREFISSI_USER)}{random.choice(SUFISSI_USER)}"

        # Design ultra-realistico: stile +rep che si fonde con lo sfondo scuro di Discord
        embed = discord.Embed(
            title=f"➕ +rep from {utente}",
            description=recensione,
            color=discord.Color.from_str("#2b2d31") # Sfondo nativo Discord Dark
        )
        embed.add_field(name="Status", value="✓ Verified Customer", inline=True)
        embed.set_footer(text="Mako Tweaks • Customer Vouch")
        embed.timestamp = datetime.now()

        await canale_recensioni.send(embed=embed)

    # Incrementa l'attesa di 29 minuti per rendere i pattern impossibili da tracciare
    bot.tempo_corrente_minuti += 29
    loop_recensioni_dinamico.change_interval(minutes=bot.tempo_corrente_minuti)

# ========================================================
# COMANDI SLASH PROTETTI (SOLO AMMINISTRATORI)
# ========================================================
@bot.tree.command(
    name="start_reviews", 
    description="Avvia il sistema di recensioni segrete.",
    default_permissions=discord.Permissions(administrator=True) # Visibile e usabile solo da admin
)
async def start_reviews(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    if loop_recensioni_dinamico.is_running():
        await interaction.followup.send("ℹ️ Sistema già attivo.", ephemeral=True)
    else:
        bot.tempo_corrente_minuti = 109
        loop_recensioni_dinamico.change_interval(minutes=bot.tempo_corrente_minuti)
        loop_recensioni_dinamico.start()
        await interaction.followup.send("✅ Configurazione applicata. Le recensioni verranno iniettate periodicamente.", ephemeral=True)

@bot.tree.command(
    name="stop_reviews", 
    description="Spegne il sistema di recensioni segrete.",
    default_permissions=discord.Permissions(administrator=True) # Visibile e usabile solo da admin
)
async def stop_reviews(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if not loop_recensioni_dinamico.is_running():
        await interaction.followup.send("ℹ️ Il sistema è già spento.", ephemeral=True)
    else:
        loop_recensioni_dinamico.stop()
        await interaction.followup.send("🛑 Sistema arrestato.", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRORE: DISCORD_TOKEN mancante.")
