using UnityEngine;
using System.Net.Sockets;
using System.IO;

public class ScreenshotSender : MonoBehaviour
{
    public Camera cameraToCapture;
    public string serverIP = "127.0.0.1"; // Localhost
    public int port = 8888;

    private TcpClient client;
    private NetworkStream stream;

    private void Start()
    {
        try
        {
            client = new TcpClient(serverIP, port);
            stream = client.GetStream();

            InvokeRepeating("SendScreenshot", 0f, 1f); // Take a screenshot every 1 second
        }
        catch (SocketException ex)
        {
            Debug.LogError("SocketException: " + ex.Message);
        }
    }

    private void SendScreenshot()
    {
        if (Camera.current == null) // Check if rendering is occurring
            return;

        Texture2D tex = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = cameraToCapture.targetTexture;
        cameraToCapture.Render();
        tex.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
        tex.Apply();
        RenderTexture.active = currentRT;

        byte[] bytes = tex.EncodeToJPG(); // Convert the texture to JPEG bytes

        Debug.Log("Sending screenshot of size: " + bytes.Length); // Add this line for debugging

        SendBytes(bytes);
    }

    private void SendBytes(byte[] bytes)
    {
        if (stream == null || !stream.CanWrite)
        {
            Debug.LogError("Stream is not writable.");
            return;
        }

        using (BinaryWriter writer = new BinaryWriter(stream))
        {
            writer.Write(bytes.Length);
            writer.Write(bytes);
        }

        Debug.Log("Screenshot sent. Size: " + bytes.Length); // Add this line for debugging
    }

    private void OnDestroy()
    {
        if (stream != null)
            stream.Close();
        if (client != null)
            client.Close();
    }
}
