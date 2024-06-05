using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using UnityEngine;

public class CameraStream : MonoBehaviour
{
    public Camera[] cameras;
    public string camIP = "127.0.0.1";
    public int basePort = 8081;
    private UdpClient[] udpClients;
    private IPEndPoint[] endPoints;
    private bool connectCam = true;
    private int frameWidth = 640;
    private int frameHeight = 480;

    void Start()
    {
        udpClients = new UdpClient[cameras.Length];
        endPoints = new IPEndPoint[cameras.Length];

        for (int i = 0; i < cameras.Length; i++)
        {
            int port = basePort + i;
            udpClients[i] = new UdpClient();
            endPoints[i] = new IPEndPoint(IPAddress.Parse(camIP), port);
            StartCoroutine(SendVideoStream(cameras[i], udpClients[i], endPoints[i]));
        }
    }

    IEnumerator SendVideoStream(Camera cam, UdpClient udpClient, IPEndPoint endPoint)
    {
        Texture2D camTexture = new Texture2D(frameWidth, frameHeight, TextureFormat.RGB24, false);
        while (connectCam)
        {
            yield return new WaitForSeconds(0.3f);

            try
            {
                RenderTexture renderTexture = new RenderTexture(frameWidth, frameHeight, 24);
                cam.targetTexture = renderTexture;
                RenderTexture.active = renderTexture;
                cam.Render();

                camTexture.ReadPixels(new Rect(0, 0, frameWidth, frameHeight), 0, 0);
                camTexture.Apply();
                cam.targetTexture = null;
                RenderTexture.active = null;
                Destroy(renderTexture);

                byte[] byteArray = camTexture.EncodeToJPG(50); // Reduce quality for faster transmission
                int chunkSize = 8192; // 8 KB chunks
                int totalChunks = Mathf.CeilToInt(byteArray.Length / (float)chunkSize);

                // Send total chunks information once
                byte[] totalChunksBytes = BitConverter.GetBytes(totalChunks);
                udpClient.Send(totalChunksBytes, totalChunksBytes.Length, endPoint);

                for (int i = 0; i < totalChunks; i++)
                {
                    int currentChunkSize = Mathf.Min(chunkSize, byteArray.Length - i * chunkSize);
                    byte[] chunk = new byte[currentChunkSize + 4];
                    Buffer.BlockCopy(BitConverter.GetBytes(i), 0, chunk, 0, 4);
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
        foreach (var udpClient in udpClients)
        {
            udpClient.Close();
        }
    }
}
