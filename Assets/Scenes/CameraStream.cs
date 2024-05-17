using System;
using System.Collections;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using UnityEngine.UI;

public class CameraStream : MonoBehaviour
{
    public Camera cam; // Reference to the Camera object in the scene
    public RawImage camImage; // UI element to display the image
    public string camIP = "127.0.0.1";
    public int camPort = 8081;
    private Texture2D camTexture; // Texture to load the image
    private UdpClient udpClient;
    private IPEndPoint endPoint;
    private bool connectCam = true;

    void Start()
    {
        camTexture = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
        udpClient = new UdpClient();
        endPoint = new IPEndPoint(IPAddress.Parse(camIP), camPort);
        StartCoroutine(SendVideoStream());
    }

    IEnumerator SendVideoStream()
    {
        while (connectCam)
        {
            yield return new WaitForSeconds(1); // wait for one second between frames

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

                // Send the image data
                udpClient.Send(byteArray, byteArray.Length, endPoint);
            }
            catch (Exception e)
            {
                Debug.LogError(e);
            }
        }
    }

    void OnApplicationQuit()
    {
        udpClient.Close();
    }
}
