using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class CarImageCapture : MonoBehaviour
{
    public Camera cam; // Reference to the Camera object in the scene
    public string savePath = "Assets/CarImages1"; // Directory to save the images
    public float captureInterval = 1f; // Time interval between captures

    private Texture2D camTexture;

    void Start()
    {
        // Ensure the save directory exists
        if (!Directory.Exists(savePath))
        {
            Directory.CreateDirectory(savePath);
        }

        camTexture = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
        StartCoroutine(CaptureImages());
    }

    IEnumerator CaptureImages()
    {
        List<Vector3> positions = new List<Vector3>
        {
            // Rear positions
            new Vector3(0, 5, -10),
            new Vector3(-2, 5, -9),
            new Vector3(2, 5, -9),

            // Rear-right corner positions
            new Vector3(5, 5, -5),
            new Vector3(4, 5, -6),
            new Vector3(6, 5, -4),

            // Right positions
            new Vector3(10, 5, 0),
            new Vector3(9, 5, -2),
            new Vector3(9, 5, 2),

            // Front-right corner positions
            new Vector3(5, 5, 5),
            new Vector3(6, 5, 4),
            new Vector3(4, 5, 6),

            // Front positions
            new Vector3(0, 5, 10),
            new Vector3(-2, 5, 9),
            new Vector3(2, 5, 9),

            // Front-left corner positions
            new Vector3(-5, 5, 5),
            new Vector3(-4, 5, 6),
            new Vector3(-6, 5, 4),

            // Left positions
            new Vector3(-10, 5, 0),
            new Vector3(-9, 5, -2),
            new Vector3(-9, 5, 2),

            // Rear-left corner positions
            new Vector3(-5, 5, -5),
            new Vector3(-6, 5, -4),
            new Vector3(-4, 5, -6),

            // Top-down positions
            new Vector3(0, 10, -10),
            new Vector3(10, 10, 0),
            new Vector3(0, 10, 10),
            new Vector3(-10, 10, 0),
            new Vector3(0, 15, 0),

            // Additional top-down angles
            new Vector3(5, 10, -5),
            new Vector3(5, 10, 5),
            new Vector3(-5, 10, 5),
            new Vector3(-5, 10, -5),

            // Ground-level positions
            new Vector3(0, 1, -10), // Rear ground level
            new Vector3(10, 1, 0),  // Right ground level
            new Vector3(0, 1, 10),  // Front ground level
            new Vector3(-10, 1, 0), // Left ground level
            new Vector3(5, 1, -10), // Rear-right ground level
            new Vector3(10, 1, 5),  // Front-right ground level
            new Vector3(5, 1, 10),  // Front-left ground level
            new Vector3(-5, 1, 10), // Front-left ground level
            new Vector3(-10, 1, -5) // Rear-left ground level
        };

        for (int i = 0; i < positions.Count; i++)
        {
            cam.transform.position = positions[i];
            cam.transform.LookAt(Vector3.zero); // Assuming the car is at the origin

            yield return new WaitForSeconds(captureInterval);

            CaptureAndSaveImage(i);
        }
    }

    void CaptureAndSaveImage(int index)
    {
        try
        {
            // Capture the camera image
            RenderTexture renderTexture = new RenderTexture(Screen.width, Screen.height, 24);
            cam.targetTexture = renderTexture;
            RenderTexture.active = renderTexture;
            cam.Render();

            camTexture.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
            camTexture.Apply();
            cam.targetTexture = null;
            RenderTexture.active = null;
            Destroy(renderTexture);

            byte[] byteArray = camTexture.EncodeToJPG();

            // Find a unique filename
            int imageIndex = 0;
            string filePath;
            do
            {
                filePath = Path.Combine(savePath, $"image_{index}_{imageIndex}.jpg");
                imageIndex++;
            } while (File.Exists(filePath));

            File.WriteAllBytes(filePath, byteArray);

            Debug.Log($"Saved image to: {filePath}");
        }
        catch (Exception e)
        {
            Debug.LogError(e);
        }
    }
}
