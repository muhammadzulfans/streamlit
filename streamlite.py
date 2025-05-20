import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

# Koneksi ke MongoDB
uri = "mongodb+srv://zenpose:capstone12345@capestone.o68xbne.mongodb.net/?retryWrites=true&w=majority&appName=capestone"
client = MongoClient(uri)
db = client.zenPoseDatabase
collection = db.yogaNewsMultiSource

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

def scrape_liputan6_yoga():
    url = "https://www.liputan6.com/tag/yoga"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    results = []

    for article in articles:
        title_tag = article.find('h4', class_='articles--iridescent-list--text-item__title')
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

def scrape_and_store():
    detik = scrape_detik_yoga()
    cnn = scrape_cnn_yoga()
    liputan6 = scrape_liputan6_yoga()

    all_data = detik + cnn + liputan6
    if all_data:
        collection.insert_many(all_data)
        print(f"✅ {len(all_data)} artikel berhasil disimpan.")
    else:
        print("⚠️ Tidak ada artikel yang ditemukan.")

def analyze_and_visualize():
    data = list(collection.find())
    if not data:
        print("⚠️ Tidak ada data dalam koleksi MongoDB.")
        return

    df = pd.DataFrame(data)
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df["hari"] = df["tanggal"].dt.day_name()
    df["jam"] = df["tanggal"].dt.hour

    # 1. Artikel Hari Ini
    hari_ini = datetime.now().date()
    df_today = df[df["tanggal"].dt.date == hari_ini]
    print(f"📅 Jumlah artikel hari ini: {len(df_today)}")

    # Histogram per jam
    if not df_today.empty:
        fig = px.histogram(df_today, x="jam", nbins=24, title="Distribusi Artikel per Jam (Hari Ini)")
        fig.show()

        # WordCloud
        text_today = " ".join(judul for judul in df_today["judul"] if pd.notnull(judul))
        custom_stopwords = set(STOPWORDS)
        custom_stopwords.update(["detik", "com", "ini", "dan", "untuk", "yang", "dengan", "karena", "jadi", "pada", "agar", "akan", "lebih", "yoga", "tag", "html", "href"])

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
        plt.show()
    else:
        print("⚠️ Tidak ada artikel untuk hari ini.")

    # Histogram per hari
    fig = px.histogram(df, x="hari", title="Distribusi Artikel per Hari")
    fig.show()

    # Tren jumlah artikel per tanggal
    df_grouped = df.groupby(df["tanggal"].dt.date).size().reset_index(name="jumlah")
    fig = px.line(df_grouped, x="tanggal", y="jumlah", title="Tren Jumlah Artikel per Hari")
    fig.show()

    # Heatmap Hari vs Jam
    pivot = df.pivot_table(index='hari', columns='jam', values='_id', aggfunc='count').fillna(0)
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot, cmap='YlGnBu', annot=True, fmt='.0f')
    plt.title("Heatmap Jumlah Artikel per Hari dan Jam")
    plt.show()

if __name__ == "__main__":
    scrape_and_store()
    analyze_and_visualize()
