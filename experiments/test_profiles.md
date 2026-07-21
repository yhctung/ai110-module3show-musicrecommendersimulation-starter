# Adversarial Test Profiles for Music Recommender

Three test profiles designed to expose edge cases and vulnerabilities in your scoring logic.

---

## Profile 1: Contradictory Mood-Energy Combination

**User wants sad music but with maximum energy (0.9)—contradicting the expected energy range for sad moods (0.2–0.6).**

```python
user_prefs = {
    "favorite_mood": "sad",
    "favorite_genre": "pop",
    "target_energy": 0.9,
    "likes_acoustic": True
}
```

**What to Check:**
- Song #5 "Gym Hero" (pop, intense, energy=0.93) should **skip entirely** (mood mismatch—"intense" not related to "sad")
- Song #12 "Melancholy Strings" (classical, sad, energy=0.25) should rank highly despite massive energy penalty
  - Mood match (+3.0) outweighs the energy mismatch
  - Acoustic: 0.95 * 0.8 = 0.76 (strong acoustic bonus helps)
- Song #8 "Night Drive Loop" (synthwave, moody, energy=0.75) should score lower than #12
  - Related mood match (+1.5) is weaker than exact match
  - Energy is outside expected range (0.2–0.6) so no energy bonus

**Why This Matters:** Tests if the mood gatekeeper is absolute and if acoustic preference amplifies good matches.

---

## Profile 2: Can Low Valence Override Mood Mismatch?

**User wants happy music. Tests if a sad song with very low valence (mood-appropriate) can compete with happy songs.**

```python
user_prefs = {
    "favorite_mood": "happy",
    "favorite_genre": "pop",
    "target_energy": 0.75,
    "likes_acoustic": False
}
```

**What to Check:**
- Song #1 "Sunrise City" (pop, happy, energy=0.82, valence=0.84)
  - Exact mood match: +3.0
  - Genre match: +1.0
  - Energy: in range (0.7–1.0) ✓, bonus: ~0.76
  - Valence: 0.84, happy mood → +0.42 bonus
  - **Score: ~5.2** (strong)
- Song #12 "Melancholy Strings" (classical, sad, energy=0.25, valence=0.35)
  - Mood: "sad" not related to "happy" → **SKIP (score=0)**
  - Should NOT appear despite having perfectly low valence for sad mood
- Song #14 "Tropical Breeze" (reggae, uplifting, energy=0.65, valence=0.76)
  - Mood: "uplifting" related to "happy" → +1.5
  - Genre: reggae vs pop → 0
  - Energy: 0.65 outside range (0.7–1.0) for "uplifting", so no energy bonus
  - Valence: 0.76, happy mood → +0.38
  - **Score: ~1.9** (much lower)

**Why This Matters:** Tests if the mood gatekeeper prevents mismatched songs from appearing, even when their valence is otherwise ideal. Valence bonus should amplify mood matches, never override the gatekeeper.

---

## Profile 3: Peaceful Music with Acoustic Preference

**User wants peaceful, chill music. Tests acoustic preference in low-energy context.**

```python
user_prefs = {
    "favorite_mood": "peaceful",
    "favorite_genre": "ambient",
    "target_energy": 0.3,
    "likes_acoustic": True
}
```

**What to Check:**
- Song #6 "Spacewalk Thoughts" (ambient, chill, energy=0.28, acousticness=0.92)
  - Mood: "chill" related to "peaceful" (both in calm group) → +1.5
  - Genre: ambient matches → +1.0
  - Energy: in range (0.2–0.4) ✓, bonus: ~0.96
  - Acoustic: 0.92 * 0.8 = 0.736
  - **Score: ~5.2** (solid, balanced match)
- Song #18 "Garden Dreams" (folk, peaceful, energy=0.32, acousticness=0.93)
  - Mood: exact "peaceful" match → +3.0
  - Genre: folk vs ambient → 0
  - Energy: in range ✓, bonus: ~0.94
  - Acoustic: 0.93 * 0.8 = 0.744
  - **Score: ~6.7** (should rank highest despite genre mismatch)
- Song #4 "Library Rain" (lofi, chill, energy=0.35, acousticness=0.86)
  - Mood: related → +1.5
  - Genre: lofi vs ambient → 0
  - Energy: in range ✓, bonus: ~0.8
  - Acoustic: 0.86 * 0.8 = 0.688
  - **Score: ~3.7** (lowest of the three)

**Why This Matters:** Tests if acoustic preference amplifies recommendations appropriately and if exact mood match (+3.0) always dominates related moods (+1.5) even with missing genre match.

---

## Running These Tests

1. Copy each profile into `main.py` as `user_prefs`
2. Run: `python src/main.py`
3. Verify:
   - Do the top 5 match your expectations?
   - Do songs with mismatched moods appear (they shouldn't)?
   - Does valence bonus amplify mood matches without breaking the gatekeeper?

## Expected Issues to Catch

- **Gatekeeper failure:** Songs with mismatched moods appearing in top-5
- **Valence over-weighting:** Low valence songs dominating despite mood mismatch
- **Weighting imbalance:** Exact mood match (+3.0) may dominate so heavily that other factors become noise
- **Acoustic preference:** Should amplify good matches but never override mood gatekeeper

