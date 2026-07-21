# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

**Mood Food v1.0**

A transparent, content-based music recommender that feeds your mood.

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

**Goal/Task:** Recommend songs to users who know what mood they want. The system suggests songs that match stated mood (e.g., "I want sad music") with secondary fine-tuning by genre, energy, and acoustic preference.

**Intended For:** Classroom exploration and learning. Users who explicitly state a mood preference and want transparent explanations for recommendations.

**Not Intended For:** Real-world production systems, popularity-based ranking, behavior-based personalization (skips, engagement), or discovering trending music.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

**Algorithm Summary:** Scores songs in three tiers. Mood is the gatekeeper: only matching or related moods pass. Genre is a tiebreaker: adds bonus to matching genres but doesn't override mood. Secondary features (energy, tempo, valence, danceability, acousticness) add small bonuses if they match preferences. Final score is sum of all tiers.

Example: User wants sad indie low-energy. Sad indie low-energy → high score. Sad folk low-energy → slightly lower (genre mismatch). Sad indie high-energy → lower (energy mismatch). Happy indie → zero (skipped, mood mismatch).

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

**Dataset Size & Features:** 20 songs from diverse genres (pop, indie, rock, electronic, hip-hop, classical, folk, ambient, lofi, reggae, synthwave, jazz, metal). Each song has: mood, genre, energy (0–1), tempo (BPM), valence (musical positivity), danceability (0–1), acousticness (0–1), title, artist.

**Limitations:** Only 20 songs means rare mood+genre combos (peaceful+electronic, intense+acoustic) have few options. No data on popularity, artist reputation, release date, or user listening history. Moods are hardcoded; new moods require code changes.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

**Works Well For:** Users with clear, conventional mood preferences (happy pop fans, sad indie lovers, chill ambient seekers). Transparent explanations show why each song was recommended.

**Patterns Captured:** Mood gatekeeper ensures sad users get sad songs, not close alternatives. Energy ranges are mood-aware: sad songs are typically slow (0.2–0.6), happy songs upbeat (0.7–1.0). Acoustic preference rewards high-acousticness songs for users who want them.

**Intuitive Results:** A user asking for "peaceful ambient with acoustic" gets calm acoustic folk and ambient songs, matching expectations.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

**Observed Behavior / Biases:**

**Energy Range Hard Boundary:** Songs outside mood-expected ranges get zero energy points (ignored, not penalized). Sad mood expects 0.2–0.6; a 0.75 song is skipped even if user targets 0.9. Filters out upbeat sad songs and slow happy songs.

**Features Not Considered:** Popularity, artist, listening history, production quality, lyrics. Only audio features and mood/genre tags are scored.

**Underrepresented Categories:** With 20 songs, rare combos (peaceful+electronic, intense+acoustic) have few options. Niche genres have limited entries.

**Genre Overfitting:** Exact mood (+3.0) dominates so much that genre barely matters. A sad classical song beats sad indie with perfect energy. Users can't prioritize genre.

---

## 7. Evaluation  

**Evaluation Process:** Tested with three adversarial user profiles designed to expose edge cases. Ran recommender on each, compared results, and verified mood gatekeeper held firm. Also tested weight shifts (doubled energy importance, halved genre) to verify mathematical robustness.

**Profiles Tested:**
1. **Contradiction:** Sad mood + high energy (0.9) + acoustic preference. Tests if mood gatekeeper holds when user preferences contradict typical conventions.
2. **Valence Bypass:** Happy mood + pop + energy 0.75. Tests if valence and danceability bonuses override the mood gatekeeper.
3. **Acoustic Integration:** Peaceful mood + ambient + energy 0.3 + acoustic preference. Tests if acoustic preference amplifies recommendations appropriately.

**What We Looked For:** Mood gatekeeper enforcement (mismatched moods skipped), secondary factors amplifying rather than overriding mood tier, weighting consistency (exact mood +3.0 always beats related mood +1.5).

**Comparisons & Insights:**

- **Profile 1 vs. 2:** Sad user (high-energy request) scores lower (4.16) than happy user (6.09). Sad+energetic is unusual, so acoustic preference (+0.76) becomes critical to bridge the gap.
- **Profile 2 vs. 3:** Folk song (5.13, exact mood) beats ambient song (4.55, right genre, related mood). Mood dominates genre—perfect mood + wrong genre > right genre + related mood.
- **Profile 1 vs. 3:** Both acoustic lovers, same bonus (~+0.75), but peaceful user (5.13) scores higher because energy aligns. Acoustic amplifies good fits; can't rescue bad energy alignment.

**Surprise:** Acoustic preference (~+0.8) is nearly worth a mood tier bonus (+1.5), and genre (+1.0) barely matters compared to mood (+3.0).

### Weight Shift Sensitivity Test

Tested robustness by doubling energy weight (max 1.0 → 2.0) and halving genre weight (1.0 → 0.5).

**Math verification:**
- Original max score: 3.0 (mood) + 1.0 (genre) + 1.0 (energy) + 0.5 (tempo) + 0.5 (valence) + 0.5 (danceability) + 0.8 (acoustic) = **7.3**
- Weight-shifted max: 3.0 + 0.5 + 2.0 + 0.5 + 0.5 + 0.5 + 0.8 = **7.8** ✓

**Results:**
- Profile 1 (Contradiction): All rankings stable; mood gatekeeper holds (avg +0.24 pts)
- Profile 2 (Valence Bypass): Ranks 3-4 reorder; energy doubling lets related-mood songs compete (avg +0.81 pts)
- Profile 3 (Acoustic Integration): All rankings stable (avg +0.78 pts)

**Key finding:** System is mathematically valid under weight shifts. Mood gatekeeper remains absolute; energy sensitivity is expected and increases diversity in related-mood tier.

### User Test Profiles Ouput

Three edge-case profiles tested to expose vulnerabilities and verify mood-gatekeeper logic:

#### Profile 1: Contradiction (Sad + High Energy + Acoustic)

```
Loaded songs: 20...

Top recommendations:

Melancholy Strings - Score: 4.16
Because: [MATCH] Exact mood match
  Energy: 0.25 vs target 0.90 -> +0.00
  Tempo: 65 BPM vs target 150 BPM -> +0.08
  Valence: 0.35 (low = good for sad mood) -> +0.33
  Acousticness: 0.95 (user prefers acoustic) -> +0.76

Night Drive Loop - Score: 2.93
Because: [RELATED] Related mood
  Energy: 0.75 vs target 0.90 -> +0.70
  Tempo: 110 BPM vs target 150 BPM -> +0.30
  Valence: 0.49 (low = good for sad mood) -> +0.26
  Acousticness: 0.22 (user prefers acoustic) -> +0.18

Midnight Blues - Score: 2.90
Because: [RELATED] Related mood
  Energy: 0.48 vs target 0.90 -> +0.16
  Tempo: 100 BPM vs target 150 BPM -> +0.25
  Valence: 0.42 (low = good for sad mood) -> +0.29
  Acousticness: 0.87 (user prefers acoustic) -> +0.70

Rainy Day Reflections - Score: 2.64
Because: [RELATED] Related mood
  Energy: 0.44 vs target 0.90 -> +0.08
  Tempo: 92 BPM vs target 150 BPM -> +0.21
  Valence: 0.52 (low = good for sad mood) -> +0.24
  Acousticness: 0.76 (user prefers acoustic) -> +0.61

Coffee Shop Stories - Score: 0.00
Because: [SKIP] Mood mismatch
```

#### Profile 2: Valence Bypass (Happy Mood)

```
Loaded songs: 20...

Top recommendations:

Sunrise City - Score: 6.09
Because: [MATCH] Exact mood match | [MATCH] Genre match
  Energy: 0.82 vs target 0.75 -> +0.86
  Tempo: 118 BPM vs target 135 BPM -> +0.41
  Valence: 0.84 (high = good for happy mood) -> +0.42
  Danceability: 0.79 (bonus for active mood) -> +0.40

Rooftop Lights - Score: 5.24
Because: [MATCH] Exact mood match
  Energy: 0.76 vs target 0.75 -> +0.98
  Tempo: 124 BPM vs target 135 BPM -> +0.45
  Valence: 0.81 (high = good for happy mood) -> +0.41
  Danceability: 0.82 (bonus for active mood) -> +0.41

Electric Dreams - Score: 3.54
Because: [RELATED] Related mood
  Energy: 0.88 vs target 0.75 -> +0.74
  Tempo: 140 BPM vs target 135 BPM -> +0.47
  Valence: 0.79 (high = good for happy mood) -> +0.40
  Danceability: 0.85 (bonus for active mood) -> +0.42

Sunset Boulevard - Score: 3.44
Because: [RELATED] Related mood
  Energy: 0.78 vs target 0.75 -> +0.94
  Tempo: 95 BPM vs target 135 BPM -> +0.30
  Valence: 0.68 (high = good for happy mood) -> +0.34
  Danceability: 0.72 (bonus for active mood) -> +0.36

Tropical Breeze - Score: 2.15
Because: [RELATED] Related mood
  Tempo: 88 BPM vs target 135 BPM -> +0.27
  Valence: 0.76 (high = good for happy mood) -> +0.38
```

#### Profile 3: Acoustic Integration (Peaceful/Ambient)

```
Loaded songs: 20...

Top recommendations:

Garden Dreams - Score: 5.13
Because: [MATCH] Exact mood match
  Energy: 0.32 vs target 0.30 -> +0.96
  Tempo: 76 BPM vs target 90 BPM -> +0.43
  Acousticness: 0.93 (user prefers acoustic) -> +0.74

Spacewalk Thoughts - Score: 4.55
Because: [RELATED] Related mood | [MATCH] Genre match
  Energy: 0.28 vs target 0.30 -> +0.96
  Tempo: 60 BPM vs target 90 BPM -> +0.35
  Acousticness: 0.92 (user prefers acoustic) -> +0.74

Coffee Shop Stories - Score: 3.57
Because: [RELATED] Related mood
  Energy: 0.37 vs target 0.30 -> +0.86
  Tempo: 90 BPM vs target 90 BPM -> +0.50
  Acousticness: 0.89 (user prefers acoustic) -> +0.71

Library Rain - Score: 3.50
Because: [RELATED] Related mood
  Energy: 0.35 vs target 0.30 -> +0.90
  Tempo: 72 BPM vs target 90 BPM -> +0.41
  Acousticness: 0.86 (user prefers acoustic) -> +0.69

Midnight Coding - Score: 3.27
Because: [RELATED] Related mood
  Energy: 0.42 vs target 0.30 -> +0.76
  Tempo: 78 BPM vs target 90 BPM -> +0.44
  Acousticness: 0.71 (user prefers acoustic) -> +0.57
```

---

## 8. Future Work  

**Ideas for Improvement:**

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

1. **Replace hard energy boundaries with soft decay.** Allow upbeat sad songs and slow happy songs to score, just with a penalty for being outside typical ranges. This solves the "contradictory but valid preferences" problem.

2. **Add a diversity penalty to the ranking.** Top-5 recommendations should sound different from each other, not all upbeat pop or all slow acoustic. Shuffle within score bands to encourage serendipity and prevent filter bubbles.

3. **Expand mood groups and allow fuzzy matching.** Support new moods (nostalgic, hopeful, angry) and handle typos. Users shouldn't be locked out because they used "nostalgic" instead of a mapped mood.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Building this recommender taught me that explainability and honesty matter more than perfection. I expected mood matching to be the hard part, but the real challenge was handling contradictory preferences gracefully. Users who want "sad but energetic" shouldn't be silently filtered out; they should get lower scores with a clear explanation of why. The most surprising discovery was how powerful acoustic preference became (+0.75 pts, nearly a mood tier bonus), revealing that secondary preferences can dominate scoring if primary factors allow it. This changed how I think about Spotify and other recommendation apps: those systems hide their trade-offs behind opaque engagement optimization, while even a simple transparent system like this one shows users why they're getting recommendations—which is arguably more respectful. This gives the user more trust.
