"""ADK tool for virtual try-on.

The agent calls try_on_product() when the user asks to try on a product.
Configure model and safety level via environment variables or design-spec.md.
"""

import os


SUPPORTED_CATEGORIES = {"clothing", "eyewear", "jewelry", "cosmetics", "footwear"}


def try_on_product(product_id: str, user_photo_uri: str, product_description: str = "") -> str:
    """Generate a virtual try-on image showing the product on the user.

    Args:
        product_id: The product to try on (must be in the catalog).
        user_photo_uri: GCS URI or base64 of the user's photo.
        product_description: Optional human-readable product name for the prompt.

    Returns:
        GCS URI of the generated try-on image, or an error message.
    """
    from app.tryon_processor import generate_tryon

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    output_bucket = os.getenv("TRYON_OUTPUT_BUCKET", "")
    upload_bucket = os.getenv("TRYON_UPLOAD_BUCKET", "")

    if not project_id or not output_bucket or not upload_bucket:
        return (
            "Try-on is not configured. Run `python scripts/setup_tryon.py` first "
            "and set GOOGLE_CLOUD_PROJECT, TRYON_OUTPUT_BUCKET, TRYON_UPLOAD_BUCKET."
        )

    try:
        result = generate_tryon(
            product_id=product_id,
            user_photo_uri=user_photo_uri,
            project_id=project_id,
            output_bucket=output_bucket,
            upload_bucket=upload_bucket,
            model_label_or_id=os.getenv("GEMINI_IMAGE_MODEL", "flash"),
            safety_level=os.getenv("TRYON_SAFETY_LEVEL", "block_most"),
            product_description=product_description,
        )
        uri = result["output_uri"]
        model = result["model_used"]
        variations = result["variations_generated"]
        return f"Try-on complete. Image: {uri} (model: {model}, {variations} variation(s) generated)"
    except Exception as e:
        return f"Try-on failed: {e}"
