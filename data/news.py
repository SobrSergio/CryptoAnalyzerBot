import requests

def get_latest_crypto_news():
    url = "https://api.coingecko.com/api/v3/news"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and isinstance(data['data'], list): 
            articles = data['data'] 
            news = []

            for article in articles[:5]: 
                if isinstance(article, dict):  
                    title = article.get("title")
                    description = article.get("description")
                    url = article.get("url")
                    if title and description and url: 
                        news.append(f"📰 <b>{title}</b>\n{description}\n<a href='{url}'>Читать далее</a>\n")
                    else:
                        continue 
                else:
                    continue 
            
            return news

        else:
            print(f"Unexpected data format: {data}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []

    except Exception as e:
        print(f"Error: {e}")
        return []
