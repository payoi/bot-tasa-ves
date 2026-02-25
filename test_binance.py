import requests

url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

payload = {
    "fiat": "VES",
    "page": 1,
    "rows": 5,
    "tradeType": "BUY",
    "asset": "USDT",
    "countries": [],
    "proMerchantAds": False,
    "shieldMerchantAds": False,
    "filterType": "all",
    "additionalKycVerifyFilter": 0,
    "publisherType": None,
    "payTypes": [],
    "classifies": ["mass", "profession", "fiat_trade"]
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

print(f"Status: {response.status_code}")
print(f"Anuncios encontrados: {len(data.get('data', []))}\n")

for i, anuncio in enumerate(data["data"], 1):
    precio = anuncio["adv"]["price"]
    vendedor = anuncio["advertiser"]["nickName"]
    print(f"  {i}. {vendedor}: Bs. {precio}")