using UnityEngine;

public class BottomLeftToOrigin : MonoBehaviour
{
    void Start()
    {
        // Get the Renderer component of the GameObject
        Renderer renderer = GetComponent<Renderer>();

        if (renderer != null)
        {
            // Calculate the bottom left corner of the GameObject in world space
            Vector3 bottomLeftCorner = renderer.bounds.min;

            // Calculate the offset to move the bottom left corner to the origin
            Vector3 offset = -bottomLeftCorner;

            // Print the offset
            Debug.Log("Offset to move bottom left corner to origin: " + offset);
        }
        else
        {
            Debug.LogError("No Renderer component found on the GameObject.");
        }
    }
}
