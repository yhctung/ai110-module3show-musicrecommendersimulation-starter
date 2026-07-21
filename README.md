# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

A mood-first content-based recommender that prioritizes explicit user intent over inferred preferences, designed to work transparently with limited user data.

---

## How The System Works

**Core Concept**: A content-based recommender that connects user preferences to song attributes by scoring how well each song matches the user's taste profile, then ranking songs by score and returning the top-k matches. Unlike engagement-optimized systems (Spotify), this system prioritizes **explicit user intent** (e.g., "I want sad songs") and **transparency** (you can see why a song was recommended).

### Features and Scoring

**Song Features** (9 audio/metadata attributes):
- `mood` — Emotional intent (sad, happy, energetic, chill, etc.)
- `genre` — Style/category (indie, pop, rock, electronic, etc.)
- `energy` — Intensity/arousal level (0–1.0 scale)
- `valence` — Musical positivity independent of mood (0–1.0 scale, minor vs. major key)
- `tempo_bpm` — Speed in beats per minute (60–160 typical range)
- `danceability` — Groove/rhythmic appeal (0–1.0 scale)
- `acousticness` — Acoustic vs. electronic instrumentation (0–1.0 scale)
- `title`, `artist` — Metadata (for display)

**User Profile** (4 explicit preferences):
- `favorite_mood` — Primary intent signal (e.g., "sad", "energetic")
- `favorite_genre` — Secondary preference (e.g., "indie", "electronic")
- `target_energy` — Desired intensity level (0–1.0 scale)
- `likes_acoustic` — Sound texture preference (boolean)

### Scoring Algorithm: Mood-First Weighting

Scores are computed in **tiers**, with mood as the gatekeeper:

**Tier 1: Mood Filtering (Foundation)**
- Exact mood match: **+3.0 points**
- Related mood match (e.g., "sad" ↔ "melancholic"): **+1.5 points**
- No mood match: **0 points (skip song)**

*Rationale:* Mood is the strongest explicit intent signal. A user seeking "sad" songs should get sad songs, regardless of other factors. This prevents the system from recommending upbeat pop just because it's popular.

**Tier 2: Genre Matching (Secondary Signal)**
- Exact genre match: **+1.0 points**
- No genre match: **+0 points (no penalty)**

*Rationale:* Genre is a secondary preference that enhances mood matching, not a filter. A great sad rock song should outrank a mediocre sad indie song. Genre serves as a tiebreaker and minor boost, not a hard requirement. This keeps mood forward: users seeking "sad" get all sad songs ranked fairly by quality, with genre as an enhancement.

**Tier 3: Secondary Features (Flexible Optimization)**

1. **Energy** (0–1.0 points)
   - Flexible range around target energy (e.g., sad songs typically 0.2–0.6, but upbeat sad songs are valid)
   - If within typical range for the mood: `max(0, 1.0 - (distance_from_target × 2))`
   - If outside typical range: no bonus (not penalized, just not rewarded)
   - *Rationale:* Users can want upbeat sad songs or slow happy songs. Energy is a preference, not a filter.

2. **Tempo** (0–0.5 points)
   - Maps target energy to expected BPM range (low energy → 60–100 BPM, high energy → 130–160 BPM)
   - Bonus if within ±30 BPM of target: `max(0, 0.5 - (distance / 60))`
   - *Rationale:* Complements energy matching; some users are tempo-sensitive.

3. **Valence** (0–0.5 points, optional)
   - For sad/melancholic moods: `(1.0 - valence) × 0.5` (reward low valence, but not required)
   - For happy/energetic moods: `valence × 0.5` (reward high valence, but not required)
   - For neutral moods: no bonus
   - *Rationale:* Valence is a nice-to-have texture that can enhance mood alignment, but the mood tag is explicit enough. This allows upbeat sad songs to score well.

4. **Danceability** (0–0.5 points, mood-dependent)
   - Only apply if mood is active (energetic, happy, confident): `danceability × 0.5`
   - For sad/chill moods: no bonus
   - *Rationale:* Danceability only matters for moods where movement is relevant.

5. **Acousticness** (0–0.8 points, preference-based)
   - If `user.likes_acoustic = True`: `acousticness × 0.8`
   - Otherwise: no bonus (don't penalize acoustic songs for non-acoustic users)
   - *Rationale:* Users who care about acoustic sound get rewarded; others are agnostic.

### Example Scoring

**Scenario: Breakup user**
```
User Profile:
  - favorite_mood: "sad"
  - favorite_genre: "indie"
  - target_energy: 0.35 (slow)
  - likes_acoustic: True

Song A: "Rainy Day Reflections" (indie, introspective, 0.44 energy, 0.52 valence, 0.76 acoustic)
  - Mood: introspective ≈ sad → +1.5 (related)
  - Genre: indie = indie → +1.0 (genre boost)
  - Energy: |0.44 - 0.35| = 0.09, within range → +0.82
  - Tempo: 92 BPM ≈ target (low energy) → +0.3
  - Valence: (1 - 0.52) × 0.5 = +0.24
  - Acousticness: 0.76 × 0.8 = +0.61
  
  TOTAL: 4.47 points → Ranked highly ✓
  Explanation: Related mood, genre match, low energy, acoustic texture

Song B: "Angry Anthem" (rock, sad, 0.88 energy, 0.42 valence, 0.10 acoustic)
  - Mood: sad = sad → +3.0 (exact match)
  - Genre: rock ≠ indie → +0 (no genre boost)
  - Energy: |0.88 - 0.35| = 0.53, outside typical range → +0 (no penalty)
  - Tempo: 160 BPM, way outside target → +0
  - Valence: (1 - 0.42) × 0.5 = +0.29
  - Acousticness: 0.10 × 0.8 = +0.08
  
  TOTAL: 3.37 points → Ranked lower than A ✓
  Explanation: Exact mood match, but higher energy than target
  
  Note: If the user had said "I want any sad music," Song B might rank higher.
  The mood is satisfied (sad ✓), but other preferences (low energy, acoustic, indie)
  are secondary to respecting the primary intent (sadness).

Song C: "Sunrise City" (pop, happy, 0.82 energy, 0.84 valence, 0.18 acoustic)
  - Mood: happy ≠ sad → 0 points (skip immediately)
  
  TOTAL: 0 points → Not recommended ✓
```

### Final Ranking

1. Score all songs using the algorithm above
2. Filter out songs with mood mismatch (score = 0)
3. Sort remaining songs by total score (descending)
4. Return top-k songs (default k=5)
5. For each recommendation, include a breakdown of which factors contributed

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

**User Profile**: favorite_genre=pop, favorite_mood=happy, target_energy=0.8, likes_acoustic=false

```
Loaded songs: 20...

Top recommendations:

Sunrise City - Score: 6.16
Because: [MATCH] Exact mood match | [MATCH] Genre match
  Energy: 0.82 vs target 0.80 -> +0.96
  Tempo: 118 BPM vs target 140 BPM -> +0.39
  Valence: 0.84 (high = good for happy mood) -> +0.42
  Danceability: 0.79 (bonus for active mood) -> +0.40

Rooftop Lights - Score: 5.16
Because: [MATCH] Exact mood match
  Energy: 0.76 vs target 0.80 -> +0.92
  Tempo: 124 BPM vs target 140 BPM -> +0.42
  Valence: 0.81 (high = good for happy mood) -> +0.41
  Danceability: 0.82 (bonus for active mood) -> +0.41

Electric Dreams - Score: 3.66
Because: [RELATED] Related mood
  Energy: 0.88 vs target 0.80 -> +0.84
  Tempo: 140 BPM vs target 140 BPM -> +0.50
  Valence: 0.79 (high = good for happy mood) -> +0.40
  Danceability: 0.85 (bonus for active mood) -> +0.42

Sunset Boulevard - Score: 3.43
Because: [RELATED] Related mood
  Energy: 0.78 vs target 0.80 -> +0.96
  Tempo: 95 BPM vs target 140 BPM -> +0.27
  Valence: 0.68 (high = good for happy mood) -> +0.34
  Danceability: 0.72 (bonus for active mood) -> +0.36

Tropical Breeze - Score: 2.12
Because: [RELATED] Related mood
  Tempo: 88 BPM vs target 140 BPM -> +0.24
  Valence: 0.76 (high = good for happy mood) -> +0.38
```

The output shows:
- **Top recommendation** ("Sunrise City") gets an exact mood and genre match, maximizing the core score
- **Secondary matches** satisfy mood but miss genre, getting lower overall scores
- **Explanation breakdown** shows how each feature contributes to the final score
- Songs are ranked by total score, with transparent reasoning for each recommendation

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Potential Biases

### Data Limitations
- **Tiny catalog** (20 songs): Real recommendations require millions of songs. Ties and limited variety are common here.
- **No lyrics/semantics**: The system doesn't understand song content, only audio features. A song with sad lyrics but happy instrumentation (high valence) might score unexpectedly.
- **Feature completeness**: Only 9 features per song. Missing context like popularity, artist reputation, release date, or cultural significance.
- **Static features**: Audio features don't capture subjective aspects like production quality, vocal tone, or narrative/story.

### Algorithm Biases

1. **Mood Gatekeeping: Missing Mood Variants**
   - **Issue**: Users must match an exact mood or a pre-defined "related" mood. New moods or typos fail silently.
   - **Impact**: Unconventional mood labels → zero recommendations
   - **Mitigation**: Expand mood relationship groups; consider fuzzy matching for typos; allow custom moods

2. **Genre as Tiebreaker, Not Filter (Mood-Forward Design)**
   - **Issue**: With genre at +1.0, mood matches in non-preferred genres can score above related mood matches in preferred genres.
   - **Impact**: Users see sad rock above sad indie if rock song has better feature alignment
   - **Acceptance**: This is intentional. Mood is primary; genre is secondary. Promotes serendipity.
   - **Trade-off**: Great for finding genre-crossing hits; frustrating for genre-purists

3. **Energy Range Soft Boundaries**
   - **Issue**: Songs outside "typical" energy ranges for a mood don't get energy points. Boundaries are somewhat arbitrary.
   - **Impact**: Upbeat sad songs don't get penalized but also don't get rewarded for energy
   - **Mitigation**: Could use soft decay instead of binary ranges

4. **Acousticness: Asymmetric Treatment**
   - **Issue**: Acoustic lovers get +0.8; non-acoustic users get +0 (no penalty). This creates a hidden bias toward acoustic music.
   - **Impact**: Over time, if the catalog is acoustic-heavy, non-acoustic users still see acoustic songs
   - **Mitigation**: Balance the catalog; or penalize acoustic songs slightly for non-acoustic users

5. **Popularity Blindness**
   - **Issue**: The system doesn't know if a song has 10M streams or 100. A hit and a niche song score the same if features match.
   - **Impact**: Niche songs rank equally to hits; users might expect some hits in recommendations
   - **Mitigation**: Add popularity/listens feature; weight it lightly (0.2–0.3 points max)

6. **Danceability Invisibility for Sad Users**
   - **Issue**: Danceability only gets points for active moods. A sad user who enjoys dancing won't see this rewarded.
   - **Impact**: Danceability is ignored for sad/chill users
   - **Mitigation**: Let users opt-in to danceability as a separate preference

7. **Valence-Lyrical Confusion**
   - **Issue**: Valence is *musical* (major vs. minor key), not *lyrical*. An upbeat sad song (high valence + sad mood) might confuse users.
   - **Impact**: Users might reject recommendations they don't understand
   - **Mitigation**: In explanations, clarify: "High valence but sad mood → upbeat instrumentation with sad lyrics"

8. **Cold Start: Sparse Genre Coverage**
   - **Issue**: If a user's favorite genre has only 1–2 songs in the catalog, they get few recommendations from their genre.
   - **Impact**: Genre fans with limited data get poor recommendations within their genre
   - **Mitigation**: Fall back to related genres when genre matches are scarce

### Fairness Considerations

- **Feature Bias**: If audio features correlate with artist demographics (e.g., certain genres dominated by certain ethnicities), this system inherits those biases.
- **Genre Stereotyping**: Users who specify genres might get stereotypical recommendations, limiting diversity and serendipity.
- **Acoustic Weighting**: Over-weighting acousticness (+0.8) favors folk, acoustic, and classical music; under-represents electronic and hip-hop.
- **No Feedback Loop**: Unlike Spotify, this system doesn't learn from user behavior (skips, replays). It can't adapt to personal taste variations over time.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



