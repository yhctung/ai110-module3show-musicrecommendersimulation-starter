"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    # user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    # user_prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}

    # ADVERSARIAL PROFILES (see ADVERSARIAL_TEST_PROFILES.md)
    contradiction = {"favorite_mood": "sad", "favorite_genre": "pop", "target_energy": 0.9, "likes_acoustic": True}
    valence_bypass = {"favorite_mood": "happy", "favorite_genre": "pop", "target_energy": 0.75, "likes_acoustic": False}
    acoustic_integration = {"favorite_mood": "peaceful", "favorite_genre": "ambient", "target_energy": 0.3, "likes_acoustic": True}

    user_prefs = acoustic_integration

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "="*80)
    print("TOP RECOMMENDATIONS FOR MOOD FOOD")
    print("="*80)

    for i, (song, score, explanation) in enumerate(recommendations, 1):
        # Extract reasoning lines
        explanation_lines = explanation.split('\n')
        tier_reason = explanation_lines[0] if explanation_lines else ""
        secondary_list = [line.strip() for line in explanation_lines[1:] if line.strip()]

        # Left side: song info (25 chars), Right side: reasoning (54 chars)
        left_width = 25
        right_width = 54

        print(f"\n┌{'─' * left_width}┬{'─' * right_width}┐")

        # Title and tier reason
        title = f"{i}. {song['title']}"
        if len(title) > left_width - 2:
            title = title[:left_width - 5] + "..."
        print(f"│ {title:<{left_width - 2}} │ {tier_reason:<{right_width - 2}} │")

        # Artist and first secondary
        artist = f"{song['artist']}"
        if secondary_list:
            secondary = secondary_list[0]
            if len(secondary) > right_width - 2:
                secondary = secondary[:right_width - 5] + "..."
            print(f"│ {artist:<{left_width - 2}} │ {secondary:<{right_width - 2}} │")
        else:
            print(f"│ {artist:<{left_width - 2}} │ {' ' * (right_width - 2)} │")

        # Mood/genre and second secondary
        mood_genre = f"{song['mood']} | {song['genre']}"
        if len(mood_genre) > left_width - 2:
            mood_genre = mood_genre[:left_width - 5] + "..."
        if len(secondary_list) > 1:
            secondary = secondary_list[1]
            if len(secondary) > right_width - 2:
                secondary = secondary[:right_width - 5] + "..."
            print(f"│ {mood_genre:<{left_width - 2}} │ {secondary:<{right_width - 2}} │")
        else:
            print(f"│ {mood_genre:<{left_width - 2}} │ {' ' * (right_width - 2)} │")

        # Score and remaining secondaries
        score_str = f"Score: {score:.2f}"
        if len(secondary_list) > 2:
            secondary = secondary_list[2]
            if len(secondary) > right_width - 2:
                secondary = secondary[:right_width - 5] + "..."
            print(f"│ {score_str:<{left_width - 2}} │ {secondary:<{right_width - 2}} │")
        else:
            print(f"│ {score_str:<{left_width - 2}} │ {' ' * (right_width - 2)} │")

        # Additional secondary reasons (if any)
        for secondary in secondary_list[3:]:
            if len(secondary) > right_width - 2:
                secondary = secondary[:right_width - 5] + "..."
            print(f"│ {' ' * (left_width - 2)} │ {secondary:<{right_width - 2}} │")

        print(f"└{'─' * left_width}┴{'─' * right_width}┘")

    # Old format (commented out)
    # print("\nTop recommendations:\n")
    # for rec in recommendations:
    #     song, score, explanation = rec
    #     print(f"{song['title']} - Score: {score:.2f}")
    #     print(f"Because: {explanation}")
    #     print()


if __name__ == "__main__":
    main()
