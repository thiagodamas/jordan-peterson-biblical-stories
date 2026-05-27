"""
Central mapping for Jordan Peterson Biblical Series transcripts project.
This is the single source of truth for all 16 lectures.
"""

from typing import TypedDict, Optional, List

class Lecture(TypedDict):
    number: int                    # 1-16 (16 = bonus)
    title: str                     # Canonical short title
    full_title: str                # Full title as it appears in sources
    mhtml_file: str                # Exact filename in sources/wayback machine/
    youtube_id: Optional[str]      # YouTube video ID (for header + thumbnail)
    keywords: List[str]            # Relevant keywords for the lecture

LECTURES: List[Lecture] = [
    {
        "number": 1,
        "title": "Introduction to the Idea of God",
        "full_title": "Biblical Series I: Introduction to the Idea of God",
        "mhtml_file": "Biblical Series I_ Introduction to the Idea of God Transcript.mhtml",
        "youtube_id": "f-wWBGo6a2w",
        "keywords": [
            "Genesis", "Evolution", "Jung", "Moral", "Testament", "Nietzsche",
            "Dostoevsky", "Divine", "Freud", "Ideology", "Abstract", "Law",
            "Pattern", "Marduk", "Chaos", "Motivation", "Consciousness"
        ],
    },
    {
        "number": 2,
        "title": "Genesis 1: Chaos and Order",
        "full_title": "Biblical Series II: Genesis 1: Chaos & Order",
        "mhtml_file": "Biblical Series II_ Genesis 1_ Chaos & Order Transcript.mhtml",
        "youtube_id": "hdrLQ7DpiWs",  # Lecture II
        "keywords": ["Genesis", "Chaos", "Order", "Creation", "Cosmology"],
    },
    {
        "number": 3,
        "title": "God and the Hierarchy of Authority",
        "full_title": "Biblical Series III: God and the Hierarchy of Authority",
        "mhtml_file": "Biblical Series III_ God and the Hierarchy of Authority Transcript.mhtml",
        "youtube_id": "R_GPAl_q2QQ",
        "keywords": ["Hierarchy", "Authority", "God", "Order", "Society"],
    },
    {
        "number": 4,
        "title": "Adam and Eve: Self-Consciousness, Evil and Death",
        "full_title": "Biblical Series IV: Adam & Eve: Self-Consciousness, Evil, & Death",
        "mhtml_file": "Bible Series IV_ Adam & Eve_ Self-Consciousness, Evil, & Death Transcript.mhtml",
        "youtube_id": "Ifi5KkXig3s",
        "keywords": ["Adam", "Eve", "Fall", "Consciousness", "Evil", "Death", "Eden"],
    },
    {
        "number": 5,
        "title": "Cain and Abel: The Hostile Brothers",
        "full_title": "Biblical Series V: Cain and Abel: The Hostile Brothers",
        "mhtml_file": "Biblical Series V_ Cain and Abel_ The Hostile Brothers Transcript.mhtml",
        "youtube_id": "44f3mxcsI50",
        "keywords": ["Cain", "Abel", "Sacrifice", "Envy", "Murder", "Brothers"],
    },
    {
        "number": 6,
        "title": "The Psychology of the Flood",
        "full_title": "Biblical Series VI: The Psychology of the Flood",
        "mhtml_file": "Biblical Series VI_ The Psychology of the Flood Transcript.mhtml",
        "youtube_id": "wNjbasba-Qw",
        "keywords": ["Noah", "Flood", "Psychology", "Catastrophe", "Renewal"],
    },
    {
        "number": 7,
        "title": "Walking with God: Noah and the Flood",
        "full_title": "Biblical Series VII: Walking with God: Noah and the Flood",
        "mhtml_file": "Biblical Series VII_ Walking with God_ Noah and the Flood Transcript.mhtml",
        "youtube_id": "6gFjB9FTN58",
        "keywords": ["Noah", "Covenant", "Obedience", "Flood", "Faith"],
    },
    {
        "number": 8,
        "title": "The Phenomenology of the Divine",
        "full_title": "Biblical Series VIII: The Phenomenology of the Divine",
        "mhtml_file": "Biblical Series VIII_ The Phenomenology of the Divine Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "UoQdp2prfmM",
        "keywords": ["Divine", "Phenomenology", "Experience", "God", "Mysticism"],
    },
    {
        "number": 9,
        "title": "The Call to Abraham",
        "full_title": "Biblical Series IX: The Call to Abraham",
        "mhtml_file": "Biblical Series IX_ The Call to Abraham Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "GmuzUZTJ0GA",
        "keywords": ["Abraham", "Call", "Faith", "Sacrifice", "Covenant"],
    },
    {
        "number": 10,
        "title": "Abraham: Father of Nations",
        "full_title": "Biblical Series X: Abraham: Father of Nations",
        "mhtml_file": "Biblical Series X_ Abraham_ Father of Nations Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "3Y6bCqT85Pc",
        "keywords": ["Abraham", "Isaac", "Nations", "Covenant", "Faith"],
    },
    {
        "number": 11,
        "title": "Sodom and Gomorrah",
        "full_title": "Biblical Series XI: Sodom and Gomorrah",
        "mhtml_file": "Biblical Series XI_ Sodom and Gomorrah Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "SKzpj0Ev8Xs",
        "keywords": ["Sodom", "Gomorrah", "Judgment", "Hospitality", "Lot"],
    },
    {
        "number": 12,
        "title": "The Great Sacrifice: Abraham and Isaac",
        "full_title": "Biblical Series XII: The Great Sacrifice: Abraham and Isaac",
        "mhtml_file": "Biblical Series XII_ The Great Sacrifice_ Abraham and Isaac Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "-yUP40gwht0",
        "keywords": ["Abraham", "Isaac", "Sacrifice", "Faith", "Binding"],
    },
    {
        "number": 13,
        "title": "Jacob's Ladder",
        "full_title": "Biblical Series XIII: Jacob's Ladder",
        "mhtml_file": "Biblical Series XIII_ Jacob's Ladder Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "A9JtQN_GoVI",
        "keywords": ["Jacob", "Ladder", "Dream", "Angels", "Bethel"],
    },
    {
        "number": 14,
        "title": "Jacob: Wrestling with God",
        "full_title": "Biblical Series XIV: Jacob: Wrestling with God",
        "mhtml_file": "Biblical Series XIV_ Jacob_ Wrestling with God Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "DRJKwDfDbco",
        "keywords": ["Jacob", "Wrestling", "Israel", "Peniel", "Transformation"],
    },
    {
        "number": 15,
        "title": "Joseph and the Coat of Many Colors",
        "full_title": "Biblical Series XV: Joseph and the Coat of Many Colors",
        "mhtml_file": "Biblical Series XV_ Joseph and the Coat of Many Colors Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "B7V8eZ1BLiI",
        "keywords": ["Joseph", "Coat", "Dreams", "Egypt", "Forgiveness", "Providence"],
    },
    {
        "number": 16,
        "title": "On the Death and Resurrection: A Psychological View",
        "full_title": "On the Death and Resurrection: A Psychological View in Five Parts",
        "mhtml_file": "On the Death and Resurrection_ A Psychological View in Five Parts Transcript _ Jordan Peterson.mhtml",
        "youtube_id": "xPIanlF6IwM",
        "keywords": ["Death", "Resurrection", "Christ", "Psychology", "Meaning"],
    },
]

def get_lecture(number: int) -> Lecture:
    """Get lecture by 1-based number (16 = bonus)."""
    for lec in LECTURES:
        if lec["number"] == number:
            return lec
    raise ValueError(f"Lecture {number} not found")

def get_mhtml_path(number: int) -> str:
    lec = get_lecture(number)
    return f"sources/wayback-machine/{lec['mhtml_file']}"

if __name__ == "__main__":
    print(f"Total lectures defined: {len(LECTURES)}")
    for lec in LECTURES:
        status = "✓" if lec["youtube_id"] else "?"
        print(f"  {lec['number']:02d}. {lec['title'][:45]:45}  {status}")
