"""
Word Encoder - Converts IP addresses and public keys to memorable word sequences
Uses PGP word list for better memorability and verification
"""

import hashlib
from typing import List


# PGP Word List (shortened version for hex encoding)
PGP_WORD_LIST_EVEN = [
    "aardvark", "absurd", "accrue", "acme", "adrift", "adult", "afflict", "ahead",
    "aimless", "algol", "allow", "alone", "ammo", "ancient", "apple", "artist",
    "assume", "athens", "atlas", "aztec", "baboon", "backfield", "backward", "banjo",
    "beaming", "bedlamp", "beehive", "beeswax", "befriend", "belfast", "berserk", "billiard",
    "bison", "blackjack", "blockade", "blowtorch", "bluebird", "bombast", "bookshelf", "brackish",
    "breadline", "breakup", "brickyard", "briefcase", "burbank", "button", "buzzard", "cement",
    "chairlift", "chatter", "checkup", "chisel", "choking", "classic", "classroom", "cleanup",
    "clockwork", "cobra", "commence", "concert", "cowbell", "crackdown", "cranky", "crowfoot",
    "crucial", "crumpled", "crusade", "cubic", "dashboard", "deadbolt", "deckhand", "dogsled",
    "dragnet", "drainage", "dreadful", "drifter", "dropper", "drumbeat", "drunken", "dupont",
    "dwelling", "eating", "edict", "egghead", "eightball", "endorse", "endow", "enlist",
    "erase", "escape", "exceed", "eyeglass", "eyetooth", "facial", "fallout", "flagpole",
    "flatfoot", "flytrap", "fracture", "framework", "freedom", "frighten", "gazelle", "geiger",
    "glitter", "glucose", "goggles", "goldfish", "gremlin", "guidance", "hamlet", "highchair",
    "hockey", "indoors", "indulge", "inverse", "involve", "island", "jawbone", "keyboard",
    "kickoff", "kiwi", "klaxon", "locale", "lockup", "merit", "minnow", "miser",
    "mohawk", "mural", "music", "necklace", "neptune", "newborn", "nightbird", "oakland",
    "obtuse", "offload", "optic", "orca", "payday", "peachy", "pheasant", "physique",
    "playhouse", "pluto", "preclude", "prefer", "preshrunk", "printer", "prowler", "pupil",
    "puppy", "python", "quadrant", "quiver", "quota", "ragtime", "ratchet", "rebirth",
    "reform", "regain", "reindeer", "rematch", "repay", "retouch", "revenge", "reward",
    "rhythm", "ribcage", "ringbolt", "robust", "rocker", "ruffled", "sailboat", "sawdust",
    "scallion", "scenic", "scorecard", "scotland", "seabird", "select", "sentence", "shadow",
    "shamrock", "showgirl", "skullcap", "skydive", "slingshot", "slowdown", "snapline", "snapshot",
    "snowcap", "snowslide", "solo", "southward", "soybean", "spaniel", "spearhead", "spellbind",
    "spheroid", "spigot", "spindle", "spyglass", "stagehand", "stairway", "standard", "stapler",
    "steamship", "sterling", "stockman", "stopwatch", "stormy", "sugar", "surmount", "suspense",
    "sweatband", "swelter", "tactics", "talon", "tapeworm", "tempest", "tiger", "tissue",
    "tonic", "topmost", "tracker", "transit", "trauma", "treadmill", "trojan", "trouble",
    "tumor", "tunnel", "tycoon", "uncut", "unearth", "unwind", "uproot", "upset",
    "upshot", "vapor", "village", "virus", "vulcan", "waffle", "wallet", "watchword",
    "wayside", "willow", "woodlark", "zulu"
]

PGP_WORD_LIST_ODD = [
    "adroitness", "adviser", "aftermath", "aggregate", "alkali", "almighty", "amulet", "amusement",
    "antenna", "applicant", "apollo", "armistice", "article", "asteroid", "atlantic", "atmosphere",
    "autopsy", "babylon", "backwater", "barbecue", "belowground", "bifocals", "bodyguard", "bookseller",
    "borderline", "bottomless", "bradbury", "bravado", "brazilian", "breakaway", "burlington", "businessman",
    "butterfat", "camelot", "candidate", "cannonball", "capricorn", "caravan", "caretaker", "celebrate",
    "cellulose", "certify", "chambermaid", "cherokee", "chicago", "clergyman", "coherence", "combustion",
    "commando", "company", "component", "concurrent", "confidence", "conformist", "congregate", "consensus",
    "consulting", "corporate", "corrosion", "councilman", "crossover", "cumbersome", "customer", "dakota",
    "decadence", "december", "decimal", "designing", "detector", "detergent", "determine", "dictator",
    "dinosaur", "direction", "disable", "disbelief", "disruptive", "distortion", "document", "embezzle",
    "enchanting", "enrollment", "enterprise", "equation", "equipment", "escapade", "everyday", "examine",
    "existence", "exodus", "fascinate", "filament", "finicky", "forever", "fortitude", "frequency",
    "gadgetry", "galveston", "getaway", "glossary", "gossamer", "graduate", "gravity", "guitarist",
    "hamburger", "hamilton", "handiwork", "hazardous", "headwaters", "hemisphere", "hesitate", "hideaway",
    "holiness", "hurricane", "hydraulic", "impartial", "impetus", "inception", "indigo", "inertia",
    "inferno", "informant", "insincere", "insurgent", "integrate", "intention", "inventive", "jamaica",
    "jupiter", "leprosy", "letterhead", "liberty", "maritime", "matchmaker", "maverick", "medusa",
    "megaton", "microscope", "microwave", "midsummer", "millionaire", "miracle", "misnomer", "molasses",
    "molecule", "montana", "monument", "mosquito", "narrative", "nebula", "newsletter", "norwegian",
    "october", "ohio", "onlooker", "opulent", "orlando", "outfielder", "pacific", "pandemic",
    "pandora", "paperweight", "paragon", "paragraph", "paramount", "passenger", "pedigree", "pegasus",
    "penetrate", "perceptive", "performance", "pharmacy", "phonetic", "photograph", "pioneer", "pocketful",
    "politeness", "positive", "potato", "processor", "provincial", "proximate", "puberty", "publisher",
    "pyramid", "quantity", "racketeer", "rebellion", "recipe", "recover", "repellent", "replica",
    "reproduce", "resistor", "responsive", "retraction", "retrieval", "retrospect", "revenue", "revival",
    "revolver", "sandalwood", "sardonic", "saturday", "savagery", "scavenger", "sensation", "sociable",
    "souvenir", "specialist", "speculate", "stethoscope", "stupendous", "supportive", "surrender", "suspicious",
    "sympathy", "tambourine", "telephone", "therapist", "tobacco", "tolerance", "tomorrow", "torpedo",
    "tradition", "travesty", "trombonist", "truncated", "typewriter", "ultimate", "undaunted", "underfoot",
    "unicorn", "unify", "universe", "unravel", "upcoming", "vacancy", "vagabond", "vertigo",
    "virginia", "visitor", "vocalist", "voyager", "warranty", "waterloo", "whimsical", "wichita",
    "wilmington", "wyoming", "yesteryear", "yucatan"
]


class WordEncoder:
    """Converts binary data to memorable word sequences"""

    @staticmethod
    def encode_hex_to_words(hex_string: str, num_words: int = 6) -> List[str]:
        """
        Convert hex string to memorable words
        Uses first N bytes of hash for consistency
        """
        # Hash the hex string for consistent length
        hash_bytes = hashlib.sha256(hex_string.encode()).digest()

        words = []
        for i in range(num_words):
            byte_val = hash_bytes[i]
            # Alternate between even and odd word lists
            if i % 2 == 0:
                word_list = PGP_WORD_LIST_EVEN
            else:
                word_list = PGP_WORD_LIST_ODD

            # Map byte to word (256 possible values, we have 256 words)
            word_idx = byte_val % len(word_list)
            words.append(word_list[word_idx])

        return words

    @staticmethod
    def encode_ip_to_words(ip_address: str) -> List[str]:
        """Convert IP address to memorable words"""
        # Create a hash of IP for word generation
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
        return WordEncoder.encode_hex_to_words(ip_hash, num_words=4)

    @staticmethod
    def encode_public_key_to_words(public_key_hex: str) -> List[str]:
        """Convert public key to memorable words for verification"""
        return WordEncoder.encode_hex_to_words(public_key_hex, num_words=8)

    @staticmethod
    def format_words_for_display(words: List[str]) -> str:
        """Format word list for display"""
        return " - ".join(words).upper()

    @staticmethod
    def create_fingerprint(public_key_hex: str, ip_address: str) -> str:
        """
        Create a human-readable fingerprint combining public key and IP
        This provides mutual trust verification
        """
        key_words = WordEncoder.encode_public_key_to_words(public_key_hex)
        ip_words = WordEncoder.encode_ip_to_words(ip_address)

        fingerprint = f"Key: {WordEncoder.format_words_for_display(key_words[:4])}\n"
        fingerprint += f"     {WordEncoder.format_words_for_display(key_words[4:])}\n"
        fingerprint += f"IP:  {WordEncoder.format_words_for_display(ip_words)}"

        return fingerprint
