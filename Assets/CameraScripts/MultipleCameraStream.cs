using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using UnityEngine;

public class CameraStream : MonoBehaviour
{
    public Camera[] cameras; // Array of camera objects
    public string camIP = "127.0.0.1";
    public int camPort = 8081;
    private UdpClient udpClient;
    private IPEndPoint endPoint;
    private bool connectCam = true;

    void Start()
    {
        udpClient = new UdpClient();
        endPoint = new IPEndPoint(IPAddress.Parse(camIP), camPort);
        foreach (Camera cam in cameras)
        {
            StartCoroutine(SendVideoStream(cam));
        }
    }

    IEnumerator SendVideoStream(Camera cam)
    {
        Texture2D camTexture = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
        while (connectCam)
        {
            yield return new WaitForSeconds(0.5f); // wait for 0.1 seconds between frames

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

                // Split the byte array into smaller chunks
                int chunkSize = 60000; // 60 KB chunks
                int totalChunks = Mathf.CeilToInt(byteArray.Length / (float)chunkSize);

                // Send the total number of chunks first
                byte[] totalChunksBytes = BitConverter.GetBytes(totalChunks);
                udpClient.Send(totalChunksBytes, totalChunksBytes.Length, endPoint);

                for (int i = 0; i < totalChunks; i++)
                {
                    int currentChunkSize = Mathf.Min(chunkSize, byteArray.Length - i * chunkSize);
                    byte[] chunk = new byte[currentChunkSize + 4];
                    Buffer.BlockCopy(BitConverter.GetBytes(i), 0, chunk, 0, 4); // Add chunk index at the start
                    Buffer.BlockCopy(byteArray, i * chunkSize, chunk, 4, currentChunkSize);

                    udpClient.Send(chunk, chunk.Length, endPoint);
                }
            }
            catch (Exception e)
            {
                Debug.LogError(e);
            }
        }
    }

    void OnApplicationQuit()
    {
        connectCam = false;
        udpClient.Close();
    }
}
