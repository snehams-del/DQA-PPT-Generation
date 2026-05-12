using UnityEngine;

public class PlaySpatialSound : MonoBehaviour
{
    public AudioClip soundEffect;
    private AudioSource audioSource;

    void Start()
    {
        // Add an AudioSource component if one doesn't exist
        audioSource = GetComponent<AudioSource>();
        if (audioSource == null)
        {
            audioSource = gameObject.AddComponent<AudioSource>();
        }

        // Set the clip
        audioSource.clip = soundEffect;

        // Configure spatial audio settings
        audioSource.spatialBlend = 1.0f; // 3D spatialization
        audioSource.rolloffMode = AudioRolloffMode.Linear; // Adjust rollOffMode as needed
        audioSource.minDistance = 1f; // Adjust minDistance as needed
        audioSource.maxDistance = 50f; // Adjust maxDistance as needed

        // Play the sound
        PlaySound();
    }

    public void PlaySound()
    {
        if (soundEffect != null)
        {
            audioSource.Play();
        }
        else
        {
            Debug.LogError("Sound effect is not assigned!");
        }
    }

    // Optionally, you can add a method to stop the sound:
    public void StopSound()
    {
        if (audioSource != null && audioSource.isPlaying)
        {
            audioSource.Stop();
        }
    }
}