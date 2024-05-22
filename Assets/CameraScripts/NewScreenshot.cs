using System.Collections;
using System.IO;
using UnityEngine;

public class CameraScreenshot : MonoBehaviour
{
    public string folderPath = "Assets/NewVehicleImages";
    private Camera _camera;

    private void Start()
    {
        _camera = GetComponent<Camera>();
        if (_camera == null)
        {
            Debug.LogError("CameraScreenshot script must be attached to a GameObject with a Camera component.");
            enabled = false;
            return;
        }

        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }

        StartCoroutine(TakeScreenshotEverySecond());
    }

    private IEnumerator TakeScreenshotEverySecond()
    {
        while (true)
        {
            yield return new WaitForSeconds(1);
            TakeScreenshot();
        }
    }

    private void TakeScreenshot()
    {
        RenderTexture renderTexture = new RenderTexture(Screen.width, Screen.height, 24);
        _camera.targetTexture = renderTexture;
        Texture2D screenShot = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
        _camera.Render();
        RenderTexture.active = renderTexture;
        screenShot.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
        _camera.targetTexture = null;
        RenderTexture.active = null;
        Destroy(renderTexture);

        byte[] bytes = screenShot.EncodeToPNG();
        string filename = string.Format("{0}/screenshot_{1}.png", folderPath, System.DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss"));
        File.WriteAllBytes(filename, bytes);

        Debug.Log(string.Format("Screenshot saved to: {0}", filename));
    }
}
