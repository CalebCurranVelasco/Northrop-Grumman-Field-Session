// using System;
// using System.Collections;
// using System.Net;
// using System.Net.Sockets;
// using UnityEngine;

// public class CameraStream : MonoBehaviour
// {
//     public Camera cam;
//     public string camIP = "127.0.0.1";
//     public int camPort = 8081;
//     private Texture2D camTexture;
//     private UdpClient udpClient;
//     private IPEndPoint endPoint;
//     private bool connectCam = true;

//     void Start()
//     {
//         camTexture = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
//         udpClient = new UdpClient();
//         endPoint = new IPEndPoint(IPAddress.Parse(camIP), camPort);
//         StartCoroutine(SendVideoStream());
//     }

//     IEnumerator SendVideoStream()
//     {
//         while (connectCam)
//         {
//             yield return new WaitForSeconds(0.3f);

//             try
//             {
//                 RenderTexture renderTexture = new RenderTexture(Screen.width, Screen.height, 24);
//                 cam.targetTexture = renderTexture;
//                 RenderTexture.active = renderTexture;
//                 cam.Render();

//                 camTexture.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
//                 camTexture.Apply();
//                 cam.targetTexture = null;
//                 RenderTexture.active = null;
//                 Destroy(renderTexture);

//                 byte[] byteArray = camTexture.EncodeToJPG();
//                 int chunkSize = 60000;
//                 int totalChunks = Mathf.CeilToInt(byteArray.Length / (float)chunkSize);

//                 for (int i = 0; i < totalChunks; i++)
//                 {
//                     int currentChunkSize = Mathf.Min(chunkSize, byteArray.Length - i * chunkSize);
//                     byte[] chunk = new byte[currentChunkSize + 8];
//                     Buffer.BlockCopy(BitConverter.GetBytes(totalChunks), 0, chunk, 0, 4); // Add totalChunks at the start
//                     Buffer.BlockCopy(BitConverter.GetBytes(i), 0, chunk, 4, 4); // Add chunk index next
//                     Buffer.BlockCopy(byteArray, i * chunkSize, chunk, 8, currentChunkSize);

//                     udpClient.Send(chunk, chunk.Length, endPoint);
//                 }
//             }
//             catch (Exception e)
//             {
//                 Debug.LogError(e);
//             }
//         }
//     }

//     void OnApplicationQuit()
//     {
//         udpClient.Close();
//     }
// }
