from domain.entities.wardrobe import TextureType

_PLURAL = {
    TextureType.SKIN: "skins",
    TextureType.CAPE: "capes"
}

def get_texture_path(file_hash: str, type: TextureType) -> str:
    return f"{_PLURAL[type]}/{file_hash[:2]}/{file_hash}"


def get_avatar_path(file_hash: str) -> str:
    return f"avatars/{file_hash[:2]}/{file_hash}"
