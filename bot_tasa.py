import requests
import time
import telebot

# --- CONFIGURACIÓN ---
TOKEN_TELEGRAM = "7933470868:AAE2vYm73cJLTcxMlLDzdVS7oE5Pe2g7xJs"
ID_CANAL = "@notiglobalve" # O el ID numérico
INTERVALO = 1800 # 30 minutos (en segundos)

bot = telebot.TeleBot(TOKEN_TELEGRAM)

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
        "tradeType": trade_type # "BUY" para Compra, "SELL" para Venta
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if data['code'] == '000000' and data['data']:
            return float(data['data'][0]['adv']['price'])
    except Exception as e:
        print(f"Error en Binance ({trade_type}): {e}")
    return None

def get_bcv_price():
    """
    Extrae el precio oficial del BCV. 
    Nota: El BCV suele bloquear scraping simple, usamos headers para parecer un navegador.
    """
    url = "https://www.bcv.org.ve/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # Nota: En un entorno de producción real, podrías necesitar una API 
        # o un scraper más avanzado si el BCV cambia su estructura.
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        # Búsqueda simple del valor del USD en el HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        dolar_seccion = soup.find(id="dolar")
        if dolar_seccion:
            precio_texto = dolar_seccion.find('strong').text.strip().replace(',', '.')
            return float(precio_texto)
    except Exception as e:
        print(f"Error obteniendo BCV: {e}")
    return None

last_price = None

def ejecutar_monitoreo():
    global last_price
    print("Consultando datos...")
    
    compra = get_binance_p2p("BUY")
    venta = get_binance_p2p("SELL")
    bcv = get_bcv_price()

    if compra and venta and bcv:
        # Cálculos
        # 1. Porcentaje de cambio (con respecto a la última ejecución)
        cambio_str = "0.00%"
        if last_price:
            diff = ((compra - last_price) / last_price) * 100
            emoji_cambio = "🔺" if diff > 0 else "🔻"
            cambio_str = f"{emoji_cambio} {abs(diff):.2f}%"
        
        # 2. Brecha con el BCV (Gap)
        brecha = ((compra - bcv) / bcv) * 100
        
        # Formateo del mensaje
        mensaje = (
            f"📊 *ACTUALIZACIÓN USDT/VES*\n"
            f"--- \n"
            f"🟢 *COMPRA:* {compra:.2f} Bs\n"
            f"🔴 *VENTA:* {venta:.2f} Bs\n"
            f"--- \n"
            f"🏦 *BCV:* {bcv:.2f} Bs\n"
            f"⚖️ *BRECHA:* {brecha:.2f}%\n"
            f"📈 *VARIACIÓN:* {cambio_str}\n"
            f"--- \n"
            f"🕒 {time.strftime('%d/%m/%Y %I:%M %p')}"
        )
        
        bot.send_message(ID_CANAL, mensaje, parse_mode="Markdown")
        last_price = compra
        print("Mensaje enviado con éxito.")
    else:
        print("No se pudieron obtener todos los datos.")

# Bucle principal
if __name__ == "__main__":
    while True:
        ejecutar_monitoreo()
        time.sleep(INTERVALO)