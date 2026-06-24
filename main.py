import os
import random
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

# ========================================================
# CONFIGURAZIONE ID
# ========================================================
ID_CANALE_RECENSIONI = 1519310548024426577  # Canale dove mandare le recensioni
ID_CANALE_LOG_FINE = 1519403485852991781    # Canale per il log di fine combinazioni
ID_RUOLO_STAFF = 1519316973614268566        # Ruolo staff per comandi

# Componenti per i nickname
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

class BotRecensioniUniche(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        
        # Liste per gestire l'univocità assoluta ed evitare ripetizioni
        self.combinazioni_rimanenti = []
        self.tempo_corrente_minuti = 109  # 1 ora e 49 minuti iniziali (60 + 49)

    def genera_tutte_le_combinazioni(self):
        """Genera tutte le permutazioni possibili e uniche dei blocchi di testo"""
        lista_totale = []
        for b1 in BLOCCO_1:
            for b2 in BLOCCO_2:
                for b3 in BLOCCO_3:
                    testo_recensione = f'"{b1}, {b2}. {b3} ⭐⭐⭐⭐⭐"'
                    lista_totale.append(testo_recensione)
        # Mescola l'ordine in modo casuale
        random.shuffle(lista_totale)
        return lista_totale

    async def setup_hook(self):
        # Carica il pool iniziale di combinazioni uniche (7 * 7 * 7 = 343 combinazioni)
        self.combinazioni_rimanenti = self.genera_tutte_le_combinazioni()
        await self.tree.sync()

    async def on_ready(self):
        print(f"🚀 Bot pronto. Combinazioni uniche caricate: {len(self.combinazioni_rimanenti)}")

bot = BotRecensioniUniche()

# ========================================================
# TASK DINAMICO CON INCREMENTO DEL TEMPO
# ========================================================
@tasks.loop(minutes=109) # Il valore iniziale viene sovrascritto dinamicamente dal codice sotto
async def loop_recensioni_dinamico():
    # Controllo immediato se ci sono ancora recensioni disponibili
    if not bot.combinazioni_rimanenti:
        canale_log = bot.get_channel(ID_CANALE_LOG_FINE)
        if canale_log:
            await canale_log.send(f"🛑 **[LOG SISTEMA]** Il bot ha terminato tutte le combinazioni uniche disponibili nel database. Il processo è stato interrotto per evitare duplicati.")
        loop_recensioni_dinamico.stop()
        return

    canale_recensioni = bot.get_channel(ID_CANALE_RECENSIONI)
    if canale_recensioni:
        # Prende ed elimina la prima recensione della lista (garantisce zero doppioni)
        recensione = bot.combinazioni_rimanenti.pop(0)
        
        # Genera un username casuale sul momento
        utente = f"{random.choice(PREFISSI_USER)}{random.choice(SUFISSI_USER)}"

        # Widget curato nei minimi dettagli (Stile feedback giallo stella)
        embed = discord.Embed(
            title="💬 Customer Feedback",
            description=recensione,
            color=discord.Color.from_str("#FEE75C")
        )
        embed.add_field(name="👤 User", value=f"`{utente}`", inline=True)
        embed.add_field(name="✅ Status", value="Verified Buyer", inline=True)
        embed.set_footer(text=f"Mako Tweaks • Remaining unique pool: {len(bot.combinazioni_rimanenti)}")
        embed.timestamp = datetime.now()

        await canale_recensioni.send(embed=embed)

    # Incrementa il timer di 29 minuti per il prossimo invio
    bot.tempo_corrente_minuti += 29
    loop_recensioni_dinamico.change_interval(minutes=bot.tempo_corrente_minuti)

# ========================================================
# COMANDI SLASH DI GESTIONE
# ========================================================
@bot.tree.command(name="start_reviews", description="Attiva il sistema di recensioni uniche e progressive.")
async def start_reviews(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    ruolo_staff = interaction.guild.get_role(ID_RUOLO_STAFF)
    
    if ruolo_staff not in interaction.user.roles:
        await interaction.followup.send("❌ Permessi insufficienti.", ephemeral=True)
        return

    if loop_recensioni_dinamico.is_running():
        await interaction.followup.send("ℹ️ Il sistema è già in esecuzione.", ephemeral=True)
    else:
        # Resetta i valori di tempo iniziali prima di partire
        bot.tempo_corrente_minuti = 109
        loop_recensioni_dinamico.change_interval(minutes=bot.tempo_corrente_minuti)
        loop_recensioni_dinamico.start()
        await interaction.followup.send(f"✅ Generatore avviato! Prima recensione inviata. Prossimo intervallo impostato a {bot.tempo_corrente_minuti} minuti (aggiunti +29m dopo ogni invio).", ephemeral=True)

@bot.tree.command(name="stop_reviews", description="Spegne manualmente il sistema.")
async def stop_reviews(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    ruolo_staff = interaction.guild.get_role(ID_RUOLO_STAFF)
    
    if ruolo_staff not in interaction.user.roles:
        await interaction.followup.send("❌ Permessi insufficienti.", ephemeral=True)
        return

    if not loop_recensioni_dinamico.is_running():
        await interaction.followup.send("ℹ️ Il sistema è già spento.", ephemeral=True)
    else:
        loop_recensioni_dinamico.stop()
        await interaction.followup.send("🛑 Generatore spento manualmente.", ephemeral=True)

# Avvio del bot su cloud (Railway)
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRORE: Variabile d'ambiente DISCORD_TOKEN non configurata.")