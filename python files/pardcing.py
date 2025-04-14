import requests

cookies = {
    'device_view': 'full',
    '_ym_uid': '1744108818360476209',
    '_ym_d': '1744108818',
    '_ym_isad': '1',
    '_ym_visorc': 'b',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    # 'cookie': 'device_view=full; _ym_uid=1744108818360476209; _ym_d=1744108818; _ym_isad=1; _ym_visorc=b',
}

response = requests.get('https://animego.ac/', cookies=cookies, headers=headers)

with open('result.html', 'w', encoding='utf-8') as file:
    file.write(response.text)

print("Successfully saved the content to result.html")