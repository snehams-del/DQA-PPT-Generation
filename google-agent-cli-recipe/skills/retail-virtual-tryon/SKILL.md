---
name: retail-virtual-tryon
description: >-
  Adds virtual try-on capabilities to a retail product search agent.
  Default uses the dedicated virtual-try-on-001 model (purpose-built,
  highest fidelity for apparel). Falls back to Gemini image generation
  (flash/pro tiers) when text-prompted variations are needed. Supports
  clothing, footwear, eyewear, jewelry, and cosmetics. Layers on top of
  retail-product-search.
deps:
  - source: retail-product-search
    type: skill
  - source: agents-cli
    type: cli
---

# Virtual Try-On

Adds virtual try-on capabilities to an existing product search agent.
Layers on top of `retail-product-search` -- only adds delta files.

Users can upload a photo and see how a product looks on them before buying.

## Execution Rules

Follow these rules strictly when executing this skill:

1. **Execute steps in order.** Do NOT jump ahead or skip steps.
2. **Verify each step succeeded** before moving to the next. If a command
   fails, stop and tell the user -- do NOT proceed.
3. **Wait for user answers.** Ask one question at a time. Do NOT assume
   defaults without confirming with the user.
4. **Confirm completion** of each step with the user before proceeding:
   "Step N is done. Ready for Step N+1?"
5. **Save all answers to `assets/design-spec.md`** as you collect them.
6. **Use the `google-genai` SDK only.** Never use `vertexai.generative_models`,
   `vertexai.preview.vision_models`, or `google.cloud.aiplatform` for Gemini calls.
   Install: `pip install --upgrade google-genai`. Route through Vertex AI by
   setting `GOOGLE_GENAI_USE_VERTEXAI=True` and using `genai.Client(vertexai=True, ...)`.
   Reference: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/overview

## When to Use

- Adding **"Try it on"** functionality to product search results
- Building **virtual fitting rooms** for fashion e-commerce
- Enabling **AR-style product visualization** (eyewear, jewelry, cosmetics)

Prerequisite: `retail-product-search` must be set up first.

Do NOT use for non-wearable products (furniture, electronics),
3D model rendering, or full-body motion capture.

## Try-On Categories

1. **Clothing** -- shirts, dresses, jackets overlaid on upper body photo
2. **Eyewear** -- glasses, sunglasses fitted to face landmarks
3. **Jewelry** -- earrings, necklaces positioned on detected features
4. **Cosmetics** -- lipstick, eyeshadow applied via face segmentation
5. **Footwear** -- shoes visualized from foot photo (limited accuracy)

## Step 1: Confirm Base Project

**V1.** Existing project path. Default: `.`

**V2.** Project name. Default: `product-search-agent`.

## Step 2: Try-On Configuration

**V3.** Which product categories support try-on? (select all that apply)
Default: Clothing + Eyewear.
Options: Clothing, Eyewear, Jewelry, Cosmetics, Footwear.

**V4.** Source of product images for try-on?
Default: GCS bucket (same as product search images).
Options: GCS bucket, Product image URLs from catalog, Upload on demand.

**V5.** Try-on image resolution?
Default: 512x512 (fast, good for preview).
Options: 256x256 (fastest), 512x512 (balanced), 1024x1024 (high quality).

## Step 3: User Photo Handling

**V6.** How will users provide their photo?
Default: Upload from device.
Options: Upload from device, Take photo with camera, Use saved profile photo.

**V7.** Store user photos for future sessions?
Default: No -- delete after session ends.
Options: Yes (requires consent + Cloud Storage), No (ephemeral only).

**V8.** Photo privacy notice?
Default: "Your photo is processed securely and not stored unless you opt in."
Ask: Should the agent display a privacy notice before requesting a photo?

## Step 4: Model Selection

Two paths -- pick based on whether you need text-driven variations.
See `references/tryon-architecture.md` in the sample project for full SDK
code examples for both paths.

### Path A: Dedicated VTO model (default -- recommended for apparel)

| Model | Label | API | Status | Best for |
|-------|-------|-----|--------|----------|
| `virtual-try-on-001` | **vto** | `client.models.recontext_image` | GA | Clothing, footwear -- "this product on this person" without text prompting. Highest fidelity, up to 4 images/request, 50 RPM regional quota. Image-only input (no text prompt). |

### Path B: Gemini image models (when text prompting needed)

| Model | Label | API | Status | Best for |
|-------|-------|-----|--------|----------|
| `gemini-2.5-flash-image` | **flash** | `client.models.generate_content` | GA | Fastest, cheapest. 1,290 tokens/img. Good for previews and iteration. |
| `gemini-3.1-flash-image-preview` | **flash-3.1** | `client.models.generate_content` | Preview | Conversational editing, multi-image fusion, character consistency. Balanced speed/quality. |
| `gemini-3-pro-image-preview` | **pro** | `client.models.generate_content` | Preview | Best quality. Reasoning-enhanced composition, legible text rendering, complex multi-turn editing. Use for hero images. |

Use Path B when you need text-driven variations ("show in red", "with a blazer over it", "outdoor setting"). VTO model does not accept text prompts.

Note: Preview models may change or be discontinued. For production, prefer GA models (`vto` or `flash`).

**V9.** Which model?
Default: `vto` (virtual-try-on-001).
Options: vto, flash, flash-3.1, pro.

Record the chosen label in `design-spec.md` → `tryon_model`.

**V10.** Number of try-on variations to generate per request?
Default: 2.
Options: 1 (fastest), 2 (balanced), 4 (more choices). Both paths support up to 4.

## Step 5: Safety and Guardrails

**V11.** Safety filter level?

| Level | Config value | Use when |
|-------|-------------|----------|
| Block most | `block_most` | Default, general retail |
| Block some | `block_some` | Fashion, activewear |
| Block few | `block_few` | Adult fashion, intimate apparel |

Default: `block_most`.

Pre-flight classifier is always enabled: it detects if the input is a product cutout vs. a real person photo before calling the generation API. This reduces false positives on white-background product images.

**V12.** Restrict to product catalog images only?
Default: Yes -- only allow try-on with products from the catalog.

## Step 6: GCP Configuration

**V13.** GCP project ID (must match product-search project).

**V14.** GCP region. Default: `us-central1`.

**V15.** GCS bucket for try-on output images. Default: `{project_id}-tryon-output`.

## Step 7: Add Files

Add these to the existing project. Do NOT re-scaffold.

```text
app/
  tryon_agent.py            # NEW: ADK tool wrapper for try-on
  tryon_processor.py        # NEW: Gemini image generation + pre-flight classifier
  agent.py                  # MODIFIED: add try_on_product tool
scripts/
  setup_tryon.py            # NEW: provision GCS buckets, verify Gemini image API
deployment/terraform/dev/
  tryon.tf                  # NEW: GCS buckets for input/output images
```

Scripts available at: `scripts/` in the sample project directory.
Sample config at: `assets/design-spec.md`.

Run setup (reads model choice from design-spec):
```bash
python scripts/setup_tryon.py --config assets/design-spec.md
```

Add this tool to the existing `agent.py`:

```python
def try_on_product(product_id: str, user_photo_uri: str) -> str:
    """Generate a virtual try-on image showing the product on the user.

    Args:
        product_id: The product to try on.
        user_photo_uri: GCS URI or base64 of the user's photo.

    Returns:
        GCS URI of the generated try-on image.
    """
    from app.tryon_processor import generate_tryon
    return generate_tryon(product_id, user_photo_uri)
```

## Step 8: Test

Test queries:
1. `"I want to try on this jacket"` -- basic try-on
2. `"Show me how these sunglasses look on me"` -- eyewear
3. `"Can I see this in a different color?"` -- variation
4. Upload a photo and ask `"Which of these dresses suits me best?"`

## Step 9: Evaluate

```bash
adk eval
```

Evalset: `evals/sets/retail-virtual-tryon.evalset.json`

Key metrics:
- Image quality (correct item shown, photorealistic overlay)
- Face/body preservation (user likeness maintained)
- Safety filter accuracy (no false positives on product cutouts)
- Latency: VTO < 4s P90, Flash < 4s P90, Pro < 7s P90

## Gotchas

- **SDK choice**: Use `google-genai` only. `vertexai.generative_models` is legacy. Replace `from vertexai.generative_models import ...` with `from google import genai`. See `references/tryon-architecture.md` in the sample project.
- **Safety false positives**: White-background product cutouts (especially swimwear/lingerie) can trigger safety blocks. The pre-flight classifier in `tryon_processor.py` detects cutouts and adjusts the safety level down one step (e.g. `block_most` to `block_some`).
- **Quota**: VTO has 50 regional RPM -- request 4 images per call instead of 4 separate calls. Gemini tiers have per-minute token limits. Monitor via Cloud Monitoring and request increases before production.
- **Photo quality**: Low-res or poorly lit user photos produce worse results. Show a quality hint in the UI.
- **Product images**: Need clean, white-background product photos for best overlay.
- **Body types**: Results vary across body types. Test diversity in your eval set.
- **Privacy**: ALWAYS inform users before processing their photo. Delete after use unless opted in. Upload bucket has 24-hour auto-delete by default.
- **Not real-time**: VTO ~3 seconds, Flash ~2 seconds, Flash 3.1 ~3 seconds, Pro ~4-6 seconds. Always show a loading indicator.
- **VTO has no text prompt**: For text-driven variations ("show in red", "outdoor scene"), use a Gemini tier instead.

## References

- `references/tryon-architecture.md` -- VTO vs Gemini paths, SDK examples, latency budget
- `references/architecture.md` (in retail-product-search sample) -- Base architecture
- `references/evaluation-guide.md` (in retail-product-search sample) -- Evaluation methodology
