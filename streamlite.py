import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import plotly.express as px


uri = "mongodb+srv://zenpose:capstone12345@capestone.o68xbne.mongodb.net/?retryWrites=true&w=majority&appName=capestone"
client = MongoClient(uri)
db = client.zenPoseDatabase
collection = db.yogaNewsMultiSource

# Detik
def scrape_detik_yoga():
    url = "https://www.detik.com/tag/yoga"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    results = []

    for article in articles:
        title_tag = article.find('h2') or article.find('h3')
        a_tag = article.find('a')
        if title_tag and a_tag:
            title = title_tag.get_text(strip=True)
            link = a_tag.get('href')
            results.append({
                "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sumber": "Detik.com",
                "judul": title,
                "url": link
            })

    return results

# CNN Indonesia
def scrape_cnn_yoga():
    url = "https://www.cnnindonesia.com/tag/yoga"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    results = []

    for article in articles:
        title_tag = article.find('h2') or article.find('h3')
        a_tag = article.find('a')
        if title_tag and a_tag:
            title = title_tag.get_text(strip=True)
            link = a_tag.get('href')
            results.append({
                "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sumber": "CNN Indonesia",
                "judul": title,
                "url": link
            })

    return results

# Liputan6
def scrape_liputan6_yoga():
    url = "https://www.liputan6.com/tag/yoga"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    results = []

    for article in articles:
        title_tag = article.find('h4', class_='articles--iridescent-list--text-item__title')  # spesifik selector Liputan6
        a_tag = article.find('a')
        if title_tag and a_tag:
            title = title_tag.get_text(strip=True)
            link = a_tag.get('href')
            results.append({
                "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sumber": "Liputan6.com",
                "judul": title,
                "url": link
            })

    return results

detik_data = scrape_detik_yoga()
cnn_data = scrape_cnn_yoga()
liputan6_data = scrape_liputan6_yoga()

all_data = detik_data + cnn_data + liputan6_data

if all_data:
    collection.insert_many(all_data)
    print(f"✅ {len(all_data)} artikel berhasil disimpan dari semua sumber.")
else:
    print("⚠️ Tidak ada data yang ditemukan.")


# Koneksi MongoDB
uri = "mongodb+srv://zenpose:capstone12345@capestone.o68xbne.mongodb.net/?retryWrites=true&w=majority&appName=capestone"
client = MongoClient(uri)
db = client.zenPoseDatabase
collection = db.detikYogaNews

# Ambil data dari MongoDB dan ubah jadi DataFrame
data = list(collection.find())
df = pd.DataFrame(data)

# Convert tanggal
df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
df["hari"] = df["tanggal"].dt.day_name()

# 1️⃣ FILTER HANYA DATA HARI INI
hari_ini = datetime.now().date()
df_today = df[df["tanggal"].dt.date == hari_ini]

print(f"📅 Jumlah artikel hari ini: {len(df_today)}")

# 2️⃣ VISUALISASI JUMLAH ARTIKEL PER JAM (dalam sehari) - PAKAI PLOTLY
if not df_today.empty:
    df_today["jam"] = df_today["tanggal"].dt.hour
    fig = px.histogram(df_today, x="jam", nbins=24, title="Distribusi Artikel per Jam (Hari Ini)")
    fig.show()

# 3️⃣ WORDCLOUD DARI JUDUL HARI INI DENGAN FILTER KATA
if not df_today.empty:
    text_today = " ".join(judul for judul in df_today["judul"])

    # Stopwords custom
    custom_stopwords = set(STOPWORDS)
    custom_stopwords.update([
        "detik", "com", "ini","dan", "untuk", "yang", "dengan",
        "karena", "jadi", "pada", "agar", "akan", "lebih",
        "yoga", "tag", "html", "href"
    ])

    # Generate WordCloud
    wordcloud = WordCloud(
        background_color="white",
        width=800,
        height=400,
        max_words=30,
        stopwords=custom_stopwords
    ).generate(text_today)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("WordCloud Judul Artikel (Hari Ini)")
    plt.savefig("wordcloud_hari_ini.png")
    plt.show()
else:
    print("⚠️ Tidak ada artikel untuk hari ini.")