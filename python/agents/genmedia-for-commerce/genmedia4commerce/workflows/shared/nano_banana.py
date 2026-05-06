import base64
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError

from workflows.shared.gemini import get_client

logger = logging.getLogger(__name__)


class NanoTimeoutError(Exception):
    """Exception raised when Nano generation times out."""

    pass


def generate_nano(
    model_name: str,
    prompt: str,
    image_bytes: bytes,
    mime_type: str = "image/png",
    timeout: int = 40,
) -> bytes:
    """Generates content using a Nano model (e.g., Image-to-Video).

    Args:
        model_name: The name of the Nano model.
        prompt: The prompt for generation.
        image_bytes: The input image as bytes.
        mime_type: The MIME type of the image.
        timeout: Maximum time in seconds to wait for generation.

    Returns:
        The generated output (e.g., video bytes).
    """
    client = get_client()

    # The API doesn't support async natively in a way that respects timeouts easily
    # for these specific Nano calls, so we use a thread pool for timeout management.
    thread_id = threading.get_ident()

    def _call_api():
        return client.models.generate_content(
            model=model_name,
            contents=[
                prompt,
                {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()},
            ],
            config={"http_options": {"api_version": "v1alpha"}},
        )

    # The API call runs in a worker thread; we wait up to `timeout` seconds.
    # If timeout is reached, we stop waiting and raise NanoTimeoutError.
    # Note: The worker thread may continue running in the background.
    logger.debug(
        f"[generate_nano] Thread {thread_id}: Calling generate_content (timeout: {timeout}s)..."
    )
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(_call_api)
        result = future.result(timeout=timeout)
    except FuturesTimeoutError as e:
        logger.error(
            f"[generate_nano] Thread {thread_id}: API call timed out after {timeout}s"
        )
        # Shutdown without waiting - let the background thread continue/die on its own
        executor.shutdown(wait=False)
        raise NanoTimeoutError(f"Nano generation timed out after {timeout} seconds") from e
    finally:
        # Only wait for cleanup if we didn't timeout
        executor.shutdown(wait=False)

    logger.debug(f"[generate_nano] Thread {thread_id}: API call completed")

    result = result.candidates[0].content.parts
    result = next(x for x in result if x.text is None).inline_data.data
    return result
