import base64
import datetime
import json

from application.dtos.minecraft_session import ProfileProperty, ProfileResponse
from domain.entities.minecraft_profile import MinecraftProfile
from domain.entities.wardrobe import SkinModel, WardrobeItem
from domain.interfaces.services.profile_signer import ProfileSigner


class MinecraftProfileService:
    def __init__(self, *, profile_signer: ProfileSigner):
        self._profile_signer = profile_signer

    def build_profile_response(
        self,
        *,
        mc_profile: MinecraftProfile,
        skin_wardrobe_item: WardrobeItem | None,
        cape_wardrobe_item: WardrobeItem | None,
    ) -> ProfileResponse:
        textures_pr_value = {
            "timestamp": int(datetime.datetime.now(datetime.UTC).timestamp()),
            "profileId": mc_profile.uuid.hex,  # .hex is without hyphens
            "profileName": mc_profile.nickname.value,
            "textures": {},
        }

        if mc_profile.active_skin_id is not None:
            textures_pr_value["textures"]["SKIN"] = {
                "url": skin_wardrobe_item.texture.url.value,
            }
            if skin_wardrobe_item.texture.model == SkinModel.SLIM:
                textures_pr_value["textures"]["SKIN"]["metadata"] = {"model": "slim"}

        if mc_profile.active_cape_id is not None:
            textures_pr_value["textures"]["CAPE"] = {
                "url": cape_wardrobe_item.texture.url.value,
            }

        textures_pr_value_b64 = base64.b64encode(json.dumps(textures_pr_value).encode()).decode()
        signature = self._profile_signer.sign(textures_pr_value_b64)
        textures_property = ProfileProperty(name="textures", value=textures_pr_value_b64, signature=signature)

        return ProfileResponse(id=mc_profile.uuid.hex, name=mc_profile.nickname.value, properties=[textures_property])
