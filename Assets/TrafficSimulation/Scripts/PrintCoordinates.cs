using UnityEngine;

public class PrintCoordinates : MonoBehaviour
{
    void Update()
    {
        Debug.Log($"{gameObject.name} Local Position: {transform.localPosition}");
        Debug.Log($"{gameObject.name} World Position: {transform.position}");
    }
}
