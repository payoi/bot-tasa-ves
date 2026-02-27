"""
BOT DE TASAS VENEZUELA
Versión: 2.1
- Publicación 1: BCV (USD/EUR) solo al actualizar
- Publicación 2: P2P USDT/VES cada 30 minutos
"""

import requests
import time
import telebot
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

TOKEN_TELEGRAM = "7933470868:AAE2vYm73cJLTcxMlLDzdVS7oE5Pe2g7xJs"  # ⚠️ Reemplaza con tu token
ID_CANAL = "@notiglobalve"
INTERVALO_BCV = 120  # 2 minutos
INTERVALO_P2P = 1800  # 30 minutos

# ═══════════════════════════════════════════════════════════════════════════════
# EMOJIS - Cambia a True cuando tengas Premium
# ═══════════════════════════════════════════════════════════════════════════════

PREMIUM = False  # Cambia a True cuando actives Premium

if PREMIUM:
    # Emojis Premium (puedes personalizarlos)
    EMOJI_BANCO = "🏛"
    EMOJI_DOLAR = "💲"
    EMOJI_EURO = "💶"
    EMOJI_SUBIDA = "📈"
    EMOJI_BAJADA = "📉"
    EMOJI_ESTABLE = "➡️"
    EMOJI_COMPRA = "🟢"
    EMOJI_VENTA = "🔴"
    EMOJI_SPREAD = "📊"
    EMOJI_BRECHA = "⚖️"
    EMOJI_FECHA = "🗓"
    EMOJI_CANAL = "📲"
else:
    # Emojis normales
    EMOJI_BANCO = "🏦"
    EMOJI_DOLAR = "💵"
    EMOJI_EURO = "💶"
    EMOJI_SUBIDA = "🔺"
    EMOJI_BAJADA = "🔻"
    EMOJI_ESTABLE = "━"
    EMOJI_COMPRA = "🟢"
    EMOJI_VENTA = "🔴"
    EMOJI_SPREAD = "📊"
    EMOJI_BRECHA = "⚖️"
    EMOJI_FECHA = "📅"
    EMOJI_CANAL = "📲"

bot = telebot.TeleBot(TOKEN_TELEGRAM)

# Variables globales
last_price = None
last_bcv_dolar = None
last_bcv_euro = None

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE OBTENCIÓN DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

def get_binance_p2p(trade_type):
    """Obtiene el mejor precio de compra o venta en Binance P2P"""
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "VES",
        "merchantCheck": True,
        "page": 1,
        "rows": 1,
        "publisherType": "merchant",
        "tradeType": trade_type
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if data['code'] == '000000' and data['data']:
            return float(data['data'][0]['adv']['price'])
    except Exception as e:
        print(f"Error en Binance ({trade_type}): {e}")
    return None


def get_bcv_prices():
    """Extrae USD y EUR del BCV"""
    url = "https://www.bcv.org.ve/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        dolar_seccion = soup.find(id="dolar")
        dolar = None
        if dolar_seccion:
            precio_texto = dolar_seccion.find('strong').text.strip().replace(',', '.')
            dolar = float(precio_texto)
        
        euro_seccion = soup.find(id="euro")
        euro = None
        if euro_seccion:
            precio_texto = euro_seccion.find('strong').text.strip().replace(',', '.')
            euro = float(precio_texto)
        
        return dolar, euro
        
    except Exception as e:
        print(f"Error obteniendo BCV: {e}")
    return None, None


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_tendencia(actual, anterior):
    """Calcula la tendencia y retorna emoji + porcentaje"""
    if anterior is None:
        return EMOJI_ESTABLE, 0
    
    diff = ((actual - anterior) / anterior) * 100
    
    if diff > 0.05:
        return EMOJI_SUBIDA, diff
    elif diff < -0.05:
        return EMOJI_BAJADA, diff
    else:
        return EMOJI_ESTABLE, diff


def hora_venezuela():
    """Retorna la hora actual de Venezuela"""
    return (datetime.utcnow() - timedelta(hours=4)).strftime('%d/%m/%Y • %I:%M %p')


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATOS DE MENSAJES
# ═══════════════════════════════════════════════════════════════════════════════

def formato_bcv(dolar, euro, tendencia_dolar, tendencia_euro):
    """Formato para actualización de BCV"""
    
    emoji_dolar, _ = tendencia_dolar
    emoji_euro, _ = tendencia_euro
    
    mensaje = f"""
{EMOJI_BANCO} *ACTUALIZACIÓN BCV*

{EMOJI_DOLAR} *Dólar:* `{dolar:.4f}` Bs {emoji_dolar}
{EMOJI_EURO} *Euro:* `{euro:.4f}` Bs {emoji_euro}

{EMOJI_FECHA} {hora_venezuela()}
{EMOJI_CANAL} *@notiglobalve*
"""
    return mensaje


def formato_p2p(compra, venta, bcv_dolar, tendencia_compra):
    """Formato para P2P con brecha respecto al BCV"""
    
    emoji_compra, diff_compra = tendencia_compra
    
    # Estado del mercado
    if diff_compra > 1:
        estado = "🟢 ALCISTA"
        icono = "📈"
    elif diff_compra < -1:
        estado = "🔴 BAJISTA"
        icono = "📉"
    else:
        estado = "🟡 ESTABLE"
        icono = "➡️"
    
    brecha = ((compra - bcv_dolar) / bcv_dolar) * 100
    spread = venta - compra
    
    if brecha > 10:
        brecha_icon = "⚠️"
    elif brecha > 5:
        brecha_icon = "📊"
    else:
        brecha_icon = "✅"
    
    mensaje = f"""
{icono} *USDT/VES* │ {estado}

💰 *BINANCE P2P*
├ {EMOJI_COMPRA} Compra: `{compra:.2f}` Bs {emoji_compra}
├ {EMOJI_VENTA} Venta: `{venta:.2f}` Bs
└ {EMOJI_SPREAD} Spread: `{spread:.2f}` Bs

{EMOJI_BRECHA} *Brecha BCV:* `{brecha:+.2f}%` {brecha_icon}

{EMOJI_FECHA} {hora_venezuela()}
{EMOJI_CANAL} *@notiglobalve*
"""
    return mensaje


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE MONITOREO
# ═══════════════════════════════════════════════════════════════════════════════

def monitorear_bcv():
    """Monitorea y publica SOLO cuando BCV actualiza"""
    global last_bcv_dolar, last_bcv_euro
    
    dolar, euro = get_bcv_prices()
    
    if dolar and euro:
        if last_bcv_dolar is None or last_bcv_euro is None:
            print("🆕 Primera lectura BCV")
            cambio = True
        elif dolar != last_bcv_dolar or euro != last_bcv_euro:
            print(f"\n{'🔔'*20}")
            print(f"🔔 ¡BCV ACTUALIZÓ!")
            print(f"   💵 USD: {last_bcv_dolar:.4f} → {dolar:.4f}")
            print(f"   💶 EUR: {last_bcv_euro:.4f} → {euro:.4f}")
            print(f"{'🔔'*20}\n")
            cambio = True
        else:
            print(f"⏳ BCV sin cambios | USD: {dolar:.4f} | EUR: {euro:.4f}")
            cambio = False
        
        if cambio:
            tendencia_dolar = calcular_tendencia(dolar, last_bcv_dolar)
            tendencia_euro = calcular_tendencia(euro, last_bcv_euro)
            
            mensaje = formato_bcv(dolar, euro, tendencia_dolar, tendencia_euro)
            
            try:
                bot.send_message(ID_CANAL, mensaje, parse_mode="Markdown")
                print(f"✅ BCV publicado | USD: {dolar:.4f} | EUR: {euro:.4f}")
                last_bcv_dolar = dolar
                last_bcv_euro = euro
            except Exception as e:
                print(f"❌ Error publicando BCV: {e}")
    else:
        print("❌ Error obteniendo BCV")


def monitorear_p2p():
    """Monitorea P2P cada 30 minutos"""
    global last_price, last_bcv_dolar
    
    print(f"\n{'─'*50}")
    print("📊 Consultando datos P2P...")
    print(f"{'─'*50}")
    
    compra = get_binance_p2p("BUY")
    venta = get_binance_p2p("SELL")
    bcv_dolar, _ = get_bcv_prices()
    
    if compra and venta and bcv_dolar:
        tendencia_compra = calcular_tendencia(compra, last_price)
        
        mensaje = formato_p2p(compra, venta, bcv_dolar, tendencia_compra)
        
        try:
            bot.send_message(ID_CANAL, mensaje, parse_mode="Markdown")
            print(f"✅ P2P publicado | Compra: {compra:.2f} Bs")
            last_price = compra
            if last_bcv_dolar is None:
                last_bcv_dolar = bcv_dolar
        except Exception as e:
            print(f"❌ Error publicando P2P: {e}")
    else:
        print("❌ Error obteniendo datos P2P")
    
    print(f"{'─'*50}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# BUCLE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*60)
    print("   🤖 BOT DE TASAS VENEZUELA v2.1")
    print("="*60)
    print(f"   📢 Canal: {ID_CANAL}")
    print(f"   ⏰ P2P: cada {INTERVALO_P2P // 60} minutos")
    print(f"   🏦 BCV: monitoreo cada {INTERVALO_BCV // 60} minutos")
    print(f"   ✨ Premium: {'Sí' if PREMIUM else 'No'}")
    print("="*60)
    print("\n🚀 Bot iniciado...\n")
    
    ciclo_count = 0
    
    while True:
        try:
            monitorear_bcv()
            
            if ciclo_count % 15 == 0:
                monitorear_p2p()
            
            ciclo_count += 1
            time.sleep(INTERVALO_BCV)
            
        except KeyboardInterrupt:
            print("\n⛔ Bot detenido por el usuario")
            break
        except Exception as e:
            print(f"❌ Error en el bucle principal: {e}")
            time.sleep(60)