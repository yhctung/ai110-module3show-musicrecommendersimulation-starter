"""
Weight shift sensitivity test: 2x energy, 0.5x genre
Compares original vs. weight-shifted scoring on all three adversarial profiles.
"""

from src.recommender import load_songs, recommend_songs, recommend_songs_weight_shifted

def test_profile(name, user_prefs):
    print(f"\n{'='*70}")
    print(f"PROFILE: {name}")
    print(f"{'='*70}")
    print(f"Preferences: {user_prefs}\n")

    songs = load_songs("data/songs.csv")

    # Original scoring
    print("ORIGINAL WEIGHTS (Genre: 1.0, Energy: max 1.0)")
    print("-" * 70)
    orig_recs = recommend_songs(user_prefs, songs, k=5)
    orig_scores = []
    for song, score, explanation in orig_recs:
        print(f"{song['title']} - Score: {score}")
        print(f"Because: {explanation}\n")
        orig_scores.append((song['title'], score))

    # Weight-shifted scoring
    print("\nWEIGHT-SHIFTED (Genre: 0.5, Energy: max 2.0)")
    print("-" * 70)
    shifted_recs = recommend_songs_weight_shifted(user_prefs, songs, k=5)
    shifted_scores = []
    for song, score, explanation in shifted_recs:
        print(f"{song['title']} - Score: {score}")
        print(f"Because: {explanation}\n")
        shifted_scores.append((song['title'], score))

    # Comparison
    print("COMPARISON")
    print("-" * 70)
    print(f"{'Song Title':<30} {'Original':<12} {'Shifted':<12} {'Change':<12}")
    print("-" * 70)

    # Build lookup
    orig_lookup = {title: score for title, score in orig_scores}
    shifted_lookup = {title: score for title, score in shifted_scores}

    # Show all unique songs from both rankings
    all_songs = set(list(orig_lookup.keys()) + list(shifted_lookup.keys()))
    for song_title in sorted(all_songs):
        orig = orig_lookup.get(song_title, 0.0)
        shifted = shifted_lookup.get(song_title, 0.0)
        change = shifted - orig
        change_str = f"{change:+.2f}" if change != 0 else "—"
        print(f"{song_title:<30} {orig:<12.2f} {shifted:<12.2f} {change_str:<12}")

    # Ranking stability
    print("\nRANKING STABILITY")
    print("-" * 70)
    for i, ((orig_title, _), (shift_title, _)) in enumerate(zip(orig_scores, shifted_scores), 1):
        status = "✓" if orig_title == shift_title else "✗ RERANKED"
        print(f"Rank {i}: {status} {orig_title}")

if __name__ == "__main__":
    # Three adversarial profiles
    contradiction = {
        "favorite_mood": "sad",
        "favorite_genre": "pop",
        "target_energy": 0.9,
        "likes_acoustic": True
    }

    valence_bypass = {
        "favorite_mood": "happy",
        "favorite_genre": "pop",
        "target_energy": 0.75,
        "likes_acoustic": False
    }

    acoustic_integration = {
        "favorite_mood": "peaceful",
        "favorite_genre": "ambient",
        "target_energy": 0.3,
        "likes_acoustic": True
    }

    test_profile("Profile 1: Contradiction", contradiction)
    test_profile("Profile 2: Valence Bypass", valence_bypass)
    test_profile("Profile 3: Acoustic Integration", acoustic_integration)

    print("\n" + "="*70)
    print("WEIGHT SHIFT SUMMARY")
    print("="*70)
    print("Genre reduced: 1.0 → 0.5 (50% reduction)")
    print("Energy increased: max 1.0 → max 2.0 (100% increase)")
    print("\nNewmax score: 3.0 (mood) + 0.5 (genre) + 2.0 (energy) + 0.5 (tempo) +")
    print("             0.5 (valence) + 0.5 (danceability) + 0.8 (acoustic) = 7.8")
    print("\nOriginal max score: 3.0 + 1.0 + 1.0 + 0.5 + 0.5 + 0.5 + 0.8 = 7.3")
    print("\nNote: New max is slightly higher due to energy doubling (1.0→2.0 change).")
