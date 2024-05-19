using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class CarImageCapture : MonoBehaviour
{
    public Camera cam; // Reference to the Camera object in the scene
    public string savePath = "Assets/CarImages2"; // Directory to save the images
    public float captureInterval = 1f; // Time interval between captures
    public int horizontalSteps = 36; // Number of steps horizontally around the car
    public int verticalSteps = 18; // Number of steps vertically from top to bottom

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
        List<Vector3> positions = GenerateSphericalPositions(Vector3.zero, 10f, horizontalSteps, verticalSteps);

        for (int i = 0; i < positions.Count; i++)
        {
            cam.transform.position = positions[i];
            cam.transform.LookAt(Vector3.zero); // Assuming the car is at the origin

            yield return new WaitForSeconds(captureInterval);

            CaptureAndSaveImage(i);
        }
    }

    List<Vector3> GenerateSphericalPositions(Vector3 center, float radius, int horizontalSteps, int verticalSteps)
    {
        List<Vector3> positions = new List<Vector3>();

        for (int v = 0; v <= verticalSteps; v++)
        {
            float verticalAngle = Mathf.PI * v / verticalSteps;
            for (int h = 0; h < horizontalSteps; h++)
            {
                float horizontalAngle = 2 * Mathf.PI * h / horizontalSteps;

                float x = center.x + radius * Mathf.Sin(verticalAngle) * Mathf.Cos(horizontalAngle);
                float y = center.y + radius * Mathf.Cos(verticalAngle);
                float z = center.z + radius * Mathf.Sin(verticalAngle) * Mathf.Sin(horizontalAngle);

                positions.Add(new Vector3(x, y, z));
            }
        }

        return positions;
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
            string filePath = Path.Combine(savePath, $"image_{index}.jpg");
            File.WriteAllBytes(filePath, byteArray);

            Debug.Log($"Saved image to: {filePath}");
        }
        catch (Exception e)
        {
            Debug.LogError(e);
        }
    }
}
