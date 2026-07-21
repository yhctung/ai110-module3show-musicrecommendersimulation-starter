from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['id'] = int(row['id'])
            row['energy'] = float(row['energy'])
            row['tempo_bpm'] = float(row['tempo_bpm'])
            row['valence'] = float(row['valence'])
            row['danceability'] = float(row['danceability'])
            row['acousticness'] = float(row['acousticness'])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}...")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str], List[str]]:
    """
    Required by recommend_songs() and src/main.py
    Scores a single song against user preferences.
    Returns (score, tier_reasons, secondary_reasons) tuple.
    """
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, tier_reasons, secondary_reasons)
    score = 0.0
    tier_reasons = []
    secondary_reasons = []

    mood_groups = {
        'sad': ['sad', 'melancholic', 'introspective', 'moody'],
        'happy': ['happy', 'uplifting', 'energetic', 'confident'],
        'calm': ['chill', 'relaxed', 'peaceful'],
        'intense': ['intense', 'aggressive', 'energetic', 'thrilling'],
    }

    # TIER 1: Mood (gatekeeper)
    target_mood = user_prefs['favorite_mood'].lower()
    song_mood = song['mood'].lower()

    if song_mood == target_mood:
        score += 3.0
        tier_reasons.append("[MATCH] Exact mood match")
    else:
        # Check if moods are related
        is_related = False
        for moods in mood_groups.values():
            if target_mood in moods and song_mood in moods:
                is_related = True
                break

        if is_related:
            score += 1.5
            tier_reasons.append("[RELATED] Related mood")
        else:
            return 0.0, ["[SKIP] Mood mismatch"], []

    # TIER 2: Genre
    target_genre = user_prefs['favorite_genre'].lower()
    song_genre = song['genre'].lower()

    if song_genre == target_genre:
        score += 1.0
        tier_reasons.append("[MATCH] Genre match")

    # TIER 3: Secondary features
    target_energy = user_prefs['target_energy']
    song_energy = song['energy']

    # Energy (with flexible range)
    mood_energy_ranges = {
        'sad': (0.2, 0.6),
        'melancholic': (0.3, 0.65),
        'introspective': (0.25, 0.55),
        'moody': (0.4, 0.8),
        'happy': (0.7, 1.0),
        'energetic': (0.8, 1.0),
        'chill': (0.2, 0.5),
        'calm': (0.2, 0.4),
        'relaxed': (0.25, 0.5),
        'peaceful': (0.2, 0.4),
        'uplifting': (0.7, 1.0),
        'confident': (0.7, 1.0),
        'intense': (0.8, 1.0),
        'aggressive': (0.8, 1.0),
        'thrilling': (0.8, 1.0),
    }

    energy_range = mood_energy_ranges.get(song_mood, (0.0, 1.0))
    if energy_range[0] <= song_energy <= energy_range[1]:
        energy_pts = max(0, 1.0 - (abs(song_energy - target_energy) * 2))
        score += energy_pts
        secondary_reasons.append(f"Energy: {song_energy:.2f} vs target {target_energy:.2f} -> +{energy_pts:.2f}")

    # Tempo (normalized to 0-1.0 scale: 60-160 BPM)
    song_tempo_norm = (song['tempo_bpm'] - 60) / 100
    target_tempo_norm = target_energy
    tempo_pts = max(0, 0.5 - (abs(song_tempo_norm - target_tempo_norm) * 0.5))
    score += tempo_pts
    if tempo_pts > 0.01:
        secondary_reasons.append(f"Tempo: {song['tempo_bpm']:.0f} BPM vs target {60 + target_energy * 100:.0f} BPM -> +{tempo_pts:.2f}")

    # Valence (mood-aligned bonus)
    sad_moods = ['sad', 'melancholic', 'introspective', 'moody', 'angry']
    happy_moods = ['happy', 'uplifting', 'energetic', 'confident']

    if song_mood in sad_moods:
        valence_pts = (1.0 - song['valence']) * 0.5
        score += valence_pts
        if valence_pts > 0.01:
            secondary_reasons.append(f"Valence: {song['valence']:.2f} (low = good for sad mood) -> +{valence_pts:.2f}")
    elif song_mood in happy_moods:
        valence_pts = song['valence'] * 0.5
        score += valence_pts
        if valence_pts > 0.01:
            secondary_reasons.append(f"Valence: {song['valence']:.2f} (high = good for happy mood) -> +{valence_pts:.2f}")

    # Danceability (active moods only)
    active_moods = ['energetic', 'happy', 'confident', 'thrilling', 'intense']
    if song_mood in active_moods:
        dance_pts = song['danceability'] * 0.5
        score += dance_pts
        if dance_pts > 0.01:
            secondary_reasons.append(f"Danceability: {song['danceability']:.2f} (bonus for active mood) -> +{dance_pts:.2f}")

    # Acousticness (preference-based)
    if user_prefs.get('likes_acoustic', False):
        acoustic_pts = song['acousticness'] * 0.8
        score += acoustic_pts
        if acoustic_pts > 0.01:
            secondary_reasons.append(f"Acousticness: {song['acousticness']:.2f} (user prefers acoustic) -> +{acoustic_pts:.2f}")

    return round(score, 2), tier_reasons, secondary_reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]

    top_k = sorted(scored, key=lambda x: (-x[1], x[0]['title']))[:k]

    result = []
    for s, sc, tier, secondary in top_k:
        tier_line = ' | '.join(tier)
        secondary_lines = '\n  '.join(secondary)
        explanation = f"{tier_line}\n  {secondary_lines}" if secondary_lines else tier_line
        result.append((s, sc, explanation))

    return result
