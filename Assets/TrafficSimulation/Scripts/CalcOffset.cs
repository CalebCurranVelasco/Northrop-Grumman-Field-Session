using UnityEngine;

public class AlignBottomLeft3D : MonoBehaviour
{
    void Start()
    {
        MeshRenderer meshRenderer = GetComponent<MeshRenderer>();
        if (meshRenderer != null)
        {
            Bounds bounds = meshRenderer.bounds;
            // Calculate the offset to move the bottom-left corner to the origin
            Vector3 offset = new Vector3(bounds.min.x, bounds.min.y, bounds.min.z);
            // Adjust the position of the object by applying the offset
            transform.position -= offset;
            Debug.Log("***************OFFSET: " + offset);
        }
        else
        {
            Debug.LogError("MeshRenderer component not found on the GameObject.");
        }
    }
}
