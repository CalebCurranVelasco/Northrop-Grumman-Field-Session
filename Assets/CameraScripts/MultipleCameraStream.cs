//using System.Collections;
//using System.Collections.Generic;
//using UnityEngine;
//using System.Net.Sockets;
//using System.Net;
//using System.Text;
//using System;

//public class CameraStream : MonoBehaviour
//{
//    public Camera cam;
//    public int width = 640;
//    public int height = 480;
//    public int port = 8081;
//    private UdpClient client;
//    private IPEndPoint endPoint;
//    private byte[] imageBytes;
//    private const int CHUNK_SIZE = 65507 - 4;  // Max UDP packet size minus 4 bytes for chunk index

//    void Start()
//    {
//        client = new UdpClient();
//        endPoint = new IPEndPoint(IPAddress.Loopback, port);
//        StartCoroutine(SendVideoStream());
//    }

//    IEnumerator SendVideoStream()
//    {
//        while (true)
//        {
//            yield return new WaitForEndOfFrame();

//            RenderTexture renderTexture = new RenderTexture(width, height, 24);
//            cam.targetTexture = renderTexture;
//            Texture2D screenShot = new Texture2D(width, height, TextureFormat.RGB24, false);
//            cam.Render();
//            RenderTexture.active = renderTexture;
//            screenShot.ReadPixels(new Rect(0, 0, width, height), 0, 0);
//            screenShot.Apply();
//            cam.targetTexture = null;
//            RenderTexture.active = null;
//            Destroy(renderTexture);

//            imageBytes = screenShot.EncodeToJPG();
//            int totalChunks = Mathf.CeilToInt((float)imageBytes.Length / CHUNK_SIZE);
//            Debug.Log($"Byte array length: {imageBytes.Length}, Total chunks: {totalChunks}");

//            // Send the total number of chunks first
//            byte[] totalChunksBytes = BitConverter.GetBytes(totalChunks);
//            client.Send(totalChunksBytes, totalChunksBytes.Length, endPoint);
//            Debug.Log($"Sent {totalChunks} chunks to {endPoint}");

//            // Send the image data in chunks
//            for (int i = 0; i < totalChunks; i++)
//            {
//                int chunkSize = (i == totalChunks - 1) ? imageBytes.Length - i * CHUNK_SIZE : CHUNK_SIZE;
//                byte[] chunkData = new byte[4 + chunkSize];
//                byte[] chunkIndexBytes = BitConverter.GetBytes(i);
//                Buffer.BlockCopy(chunkIndexBytes, 0, chunkData, 0, 4);
//                Buffer.BlockCopy(imageBytes, i * CHUNK_SIZE, chunkData, 4, chunkSize);

//                client.Send(chunkData, chunkData.Length, endPoint);
//                Debug.Log($"Sent chunk {i + 1}/{totalChunks} to {endPoint}");
//            }
//        }
//    }
//}
