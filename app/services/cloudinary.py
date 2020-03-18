import os
import time
import secrets

import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary import CloudinaryImage
from cloudinary.utils import cloudinary_url
from loguru import logger

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


def upload_image_to_cloudinary(file_url: str, username: str) -> str:
    """Upload image to cloudinary and return the secure url."""
    logger.info(f"Uploading image with local url: {file_url} ...")

    upload_result = cloudinary.uploader.upload(
        file_url,
        public_id=f"profile_pics/{username}-{secrets.token_hex(16)}",
        asset_folder="profile_pics",
        resource_type="image",
        overwrite=True,
        eager=[{"width": 100, "height": 100, "crop": "fill", "radius": 50, "effect": "sepia"}],
    )

    # TODO: Was not able to get the image to update. Maybe there is a better way to transform the image.

    # transformed_url = CloudinaryImage(public_id=f"profile_pics/{username}").build_url(width=100, height=100, crop="fill")

    # transformed_url, options = cloudinary_url(
    #     upload_result["public_id"],
    #     # format="jpg",
    #     crop="fill",
    #     width=100,
    #     height=100,
    #     radius=50,
    #     effect="sepia"
    # )
    # transformed_url += f"?t={int(time.time())}"

    # logger.error(options)

    # logger.debug(transformed_url)

    # return upload_result["secure_url"]

    return upload_result["eager"][0]["url"]


def delete_images_from_cloudinary(public_id: str):
    """Delete image from cloudinary."""
    image_delete_result = cloudinary.api.delete_resources(
        public_ids=[public_id],
        resource_type="image",
        type="upload",
    )

    logger.debug(image_delete_result)
