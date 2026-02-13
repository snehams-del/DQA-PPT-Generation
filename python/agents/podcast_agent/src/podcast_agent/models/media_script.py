from typing import List
from pydantic import BaseModel, Field

class SpeakerProfile(BaseModel):
    """Configuration for an individual speaker or character."""
    speaker_id: str = Field(..., description="Unique identifier for the speaker (e.g., 'host_1').")
    name: str = Field(..., description="The name of the speaker to be used for logging or display.")

class ScriptSegment(BaseModel):
    """A single unit of dialogue or narration."""
    speaker_id: str = Field(..., description="Matches a speaker_id defined in the speakers list.")
    text: str = Field(..., description="The actual text to be spoken by this speaker.")

class MediaScript(BaseModel):
    """The full payload containing all speakers and the sequence of dialogue."""
    speakers: List[SpeakerProfile]
    segments: List[ScriptSegment]
