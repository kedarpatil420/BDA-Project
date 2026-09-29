"""
src/bloom_filter.py
-------------------
Custom Bloom Filter implementation using double hashing.

A Bloom Filter is a space-efficient probabilistic data structure that tests
whether an element is a member of a set.  It can return two answers:
  - "Definitely NOT in the set"  (no false negatives)
  - "Probably IN the set"        (small probability of false positives)

Double Hashing Technique
------------------------
To generate k independent hash positions from two base hash functions:
    h_i(x) = (h1(x) + i * h2(x))  mod  m    for i = 0, 1, ..., k-1

where:
    h1  is derived from SHA-256
    h2  is derived from MD5
    m   is the bit array size
    k   is the number of hash functions

Optimal Parameters
------------------
Given n expected items and desired false-positive rate p:
    m = ceil( -n * ln(p) / (ln 2)^2 )   (optimal bit array size)
    k = ceil( (m / n) * ln 2 )           (optimal number of hash functions)
"""

import hashlib
import math


class BloomFilter:
    """
    Space-efficient probabilistic membership testing structure.

    Parameters
    ----------
    n : int
        Expected number of elements to be inserted.
    false_positive_rate : float
        Desired false-positive probability (e.g. 0.01 = 1 %).
    """

    def __init__(self, n: int, false_positive_rate: float = 0.01):
        self.n   = n
        self.fpr = false_positive_rate

        # Optimal bit array size
        self.m = math.ceil(
            -n * math.log(false_positive_rate) / (math.log(2) ** 2)
        )

        # Optimal number of hash functions
        self.k = math.ceil((self.m / n) * math.log(2))

        # Bit array stored as a bytearray (ceil(m/8) bytes)
        self.bit_array = bytearray(math.ceil(self.m / 8))
        self.count = 0          # number of items inserted

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _hash_positions(self, item: str) -> list:
        """
        Generate k bit positions using double hashing.

        h_i(x) = (h1(x) + i * h2(x)) mod m
        """
        encoded = str(item).encode('utf-8')
        h1 = int(hashlib.sha256(encoded).hexdigest(), 16) % self.m
        h2 = int(hashlib.md5(encoded).hexdigest(),    16) % self.m
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def _set_bit(self, pos: int):
        """Set bit at position pos to 1."""
        self.bit_array[pos // 8] |= (1 << (pos % 8))

    def _get_bit(self, pos: int) -> int:
        """Return the bit value (0 or 1) at position pos."""
        return (self.bit_array[pos // 8] >> (pos % 8)) & 1

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def add(self, item: str):
        """Insert an item into the Bloom Filter."""
        for pos in self._hash_positions(item):
            self._set_bit(pos)
        self.count += 1

    def check(self, item: str) -> bool:
        """
        Test membership.

        Returns
        -------
        bool
            True  -> item is PROBABLY in the set (possible false positive)
            False -> item is DEFINITELY NOT in the set (no false negatives)
        """
        return all(self._get_bit(pos) for pos in self._hash_positions(item))

    @property
    def actual_fpr(self) -> float:
        """
        Compute the theoretical false-positive rate given the number of
        items actually inserted.

            FPR = (1 - e^(-k*n/m))^k
        """
        return (1 - math.exp(-self.k * self.count / self.m)) ** self.k

    def info(self) -> dict:
        """Return a summary dict of filter parameters."""
        return {
            'bit_array_size_bits'  : self.m,
            'bit_array_size_bytes' : len(self.bit_array),
            'num_hash_functions'   : self.k,
            'items_inserted'       : self.count,
            'target_fpr_pct'       : round(self.fpr * 100, 2),
            'actual_fpr_pct'       : round(self.actual_fpr * 100, 4),
        }


def run_bloom_filter_demo(titles: list) -> dict:
    """
    Build a Bloom Filter from all Netflix titles, then test membership
    for a set of known (present) and unknown (absent) titles.

    Parameters
    ----------
    titles : list
        List of title strings from the cleaned dataset.

    Returns
    -------
    dict
        Contains filter info, known-title test results, and unknown-title results.
    """
    # Build filter with 1 % target false-positive rate
    bf = BloomFilter(n=len(titles), false_positive_rate=0.01)
    for title in titles:
        bf.add(title)

    # Known titles — must all return True
    known = [
        "Squid Game",
        "Stranger Things",
        "The Crown",
        "Breaking Bad",
        "Bird Box",
    ]

    # Unknown titles — should all return False (very occasionally a false positive)
    unknown = [
        "NotANetflixTitle_XYZ_001",
        "FakeShow_BDA_2099",
        "GhostSeries_Imaginary_ABC",
        "NonExistentFilm_999",
        "PlaceholderTitle_ZZZ",
    ]

    # Adjust known list: keep only titles that are actually in the dataset
    present_known   = [t for t in known   if t in set(titles)]
    # If some known titles aren't found (dataset variant), sample from actual titles
    if len(present_known) < 5:
        import random
        random.seed(42)
        supplement = random.sample(titles, 5 - len(present_known))
        present_known += supplement

    known_results   = [(t, bf.check(t)) for t in present_known[:5]]
    unknown_results = [(t, bf.check(t)) for t in unknown]

    return {
        'filter_info'    : bf.info(),
        'known_results'  : known_results,
        'unknown_results': unknown_results,
    }
