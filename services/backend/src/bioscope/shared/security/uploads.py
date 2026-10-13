"""File checks that run before private local object storage accepts bytes."""

from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError

from bioscope.shared.domain.errors import UploadRejected

ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image_upload(*, content: bytes, content_type: str, max_upload_mb: int) -> None:
    """Validate MIME, image decodability, dimensions, and a bounded payload size."""

    if content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise UploadRejected("Only JPEG, PNG, and WebP images are accepted.")
    if not content:
        raise UploadRejected("The uploaded file is empty.")
    if len(content) > max_upload_mb * 1024 * 1024:
        raise UploadRejected("The uploaded file exceeds the configured size limit.")
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
        with Image.open(BytesIO(content)) as image:
            width, height = image.size
    except (OSError, UnidentifiedImageError) as exc:
        raise UploadRejected("The uploaded file is not a valid image.") from exc
    if width < 16 or height < 16 or width * height > 40_000_000:
        raise UploadRejected("The image dimensions are outside the permitted range.")
