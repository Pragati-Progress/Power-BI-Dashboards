import pandas as pd
import requests
import time
from urllib.parse import quote_plus

# ========== STEP 1: FILL YOUR CREDENTIALS ==========
CLIENT_ID = "b5fd2cc90c9d455e9eb62b296cf8d8a5"
CLIENT_SECRET = "4dd4fbc8e19a45f882649b839e9f6f0e"

# ========== STEP 2: SPOTIFY AUTHENTICATION ==========
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    response.raise_for_status()
    return response.json()['access_token']

# ========== STEP 3: SEARCH TRACK ==========
def search_track(track_name, artist_name, token):
    query = quote_plus(f"{track_name} {artist_name}")
    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, None, None
    data = response.json()
    if data['tracks']['items']:
        track = data['tracks']['items'][0]
        return (
            track['id'],
            track['external_urls']['spotify'],
            track['album']['images'][0]['url'] if track['album']['images'] else None
        )
    return None, None, None

# ========== STEP 4: MAIN FUNCTION ==========
def enrich_tracks(csv_path, output_path):
    df = pd.read_csv(csv_path, encoding='ISO-8859-1')
    token = get_spotify_token(CLIENT_ID, CLIENT_SECRET)

    track_ids = []
    track_urls = []
    album_images = []

    for index, row in df.iterrows():
        track_name = str(row['track_name'])
        artist_name = str(row['artist(s)_name'])
        track_id, track_url, album_image = search_track(track_name, artist_name, token)

        track_ids.append(track_id)
        track_urls.append(track_url)
        album_images.append(album_image)

        print(f"[{index+1}/{len(df)}] {track_name} by {artist_name} — {'Found' if track_id else 'Not Found'}")
        time.sleep(0.3)  # Respect Spotify rate limits

    df['spotify_track_id'] = track_ids
    df['spotify_url'] = track_urls
    df['album_image_url'] = album_images

    df.to_csv(output_path, index=False)
    print(f"\n✅ Done! Enriched data saved to {output_path}")

# ========== USAGE ==========
if __name__ == "__main__":
    enrich_tracks("spotify-2023.csv", "spotify-2023-enriched.csv")
