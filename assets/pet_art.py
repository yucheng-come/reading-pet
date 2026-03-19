"""宠物 Emoji 字典"""

PET_EMOJIS = {
    "egg": "🥚",
    "cat": {
        "baby": "🐱",
        "teen": "😺",
        "adult": "😸",
        "legend": "👑🐱",
    },
    "dog": {
        "baby": "🐶",
        "teen": "🐕",
        "adult": "🦮",
        "legend": "👑🐶",
    },
    "dragon": {
        "baby": "🐲",
        "teen": "🐉",
        "adult": "🐲",
        "legend": "👑🐉",
    },
}

STATUS_EMOJIS = {
    "normal": "😊",
    "hungry": "😿",
    "runaway": "💨",
}


def get_pet_emoji(pet_type: str | None, emoji_key: str) -> str:
    if emoji_key == "egg":
        return PET_EMOJIS["egg"]
    if pet_type is None:
        return PET_EMOJIS["egg"]
    type_emojis = PET_EMOJIS.get(pet_type, PET_EMOJIS["cat"])
    return type_emojis.get(emoji_key, "❓")
