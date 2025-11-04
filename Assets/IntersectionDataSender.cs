using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Collections.Generic;
using TrafficSimulation;

/// <summary>
/// Sends intersection positions to Python for strategic police positioning
/// Sends once at startup, then Python uses this data for chokepoint detection
/// </summary>
public class IntersectionDataSender : MonoBehaviour
{
    [Header("Network Settings")]
    [Tooltip("Python receiver IP address")]
    public string pythonIP = "127.0.0.1";

    [Tooltip("Python receiver port for intersection data")]
    public int intersectionDataPort = 15001;

    [Header("Traffic System")]
    [Tooltip("Reference to the TrafficSystem in the scene")]
    public TrafficSystem trafficSystem;

    private UdpClient udpClient;

    void Start()
    {
        // Initialize UDP client
        udpClient = new UdpClient();

        // Wait a moment for everything to initialize, then send intersection data
        Invoke("SendIntersectionData", 1.0f);

        // Send periodically to ensure Python receives it (in case Python starts late)
        InvokeRepeating("SendIntersectionData", 2.0f, 5.0f);  // Send every 5 seconds
    }

    void SendIntersectionData()
    {
        Debug.Log("=== SendIntersectionData called ===");

        if (trafficSystem == null)
        {
            Debug.LogError("❌ TrafficSystem reference not set! Please assign it in the Inspector.");
            return;
        }

        Debug.Log($"✓ TrafficSystem found: {trafficSystem.name}");

        // Get all intersections from the traffic system
        Intersection[] intersections = trafficSystem.GetComponentsInChildren<Intersection>();

        Debug.Log($"Found {intersections.Length} intersections in TrafficSystem");

        if (intersections.Length == 0)
        {
            Debug.LogWarning("⚠️ No intersections found in TrafficSystem!");
            return;
        }

        // Build JSON with intersection data
        List<IntersectionData> intersectionList = new List<IntersectionData>();

        foreach (Intersection intersection in intersections)
        {
            Vector3 worldPos = intersection.transform.position;

            // Convert world coordinates to camera pixel coordinates
            // We'll use the same cameras as in the tracking system
            Camera camera1 = GameObject.Find("BirdsEyeCamera1")?.GetComponent<Camera>();
            Camera camera2 = GameObject.Find("BirdsEyeCamera2")?.GetComponent<Camera>();

            IntersectionData intersectionData = new IntersectionData
            {
                id = intersection.id,
                world_x = worldPos.x,
                world_y = worldPos.y,
                world_z = worldPos.z,
                type = intersection.intersectionType.ToString()
            };

            // Add camera-specific pixel coordinates if cameras are found
            if (camera1 != null)
            {
                Vector3 screenPos1 = WorldToScreenPoint(camera1, worldPos);
                intersectionData.camera1_x = (int)screenPos1.x;
                intersectionData.camera1_y = (int)screenPos1.y;
            }
            else
            {
                Debug.LogWarning("⚠️ BirdsEyeCamera1 not found!");
            }

            if (camera2 != null)
            {
                Vector3 screenPos2 = WorldToScreenPoint(camera2, worldPos);
                intersectionData.camera2_x = (int)screenPos2.x;
                intersectionData.camera2_y = (int)screenPos2.y;
            }
            else
            {
                Debug.LogWarning("⚠️ BirdsEyeCamera2 not found!");
            }

            intersectionList.Add(intersectionData);
        }

        Debug.Log($"Built intersection list with {intersectionList.Count} entries");

        // Create JSON message
        IntersectionMessage message = new IntersectionMessage
        {
            message_type = "intersection_data",
            intersections = intersectionList.ToArray()
        };

        string json = JsonUtility.ToJson(message, true);

        // Send to Python
        byte[] data = Encoding.UTF8.GetBytes(json);
        try
        {
            udpClient.Send(data, data.Length, pythonIP, intersectionDataPort);
            Debug.Log($"✓ Sent {intersectionList.Count} intersections to Python at {pythonIP}:{intersectionDataPort}");
            Debug.Log($"Intersection data preview:\n{json.Substring(0, Mathf.Min(500, json.Length))}...");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to send intersection data: {e.Message}");
        }
    }

    Vector3 WorldToScreenPoint(Camera camera, Vector3 worldPos)
    {
        Vector3 screenPoint = camera.WorldToScreenPoint(worldPos);

        // Flip y-coordinate to match Python's coordinate system
        screenPoint.y = camera.pixelHeight - screenPoint.y;

        return screenPoint;
    }

    void OnDestroy()
    {
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }

    // JSON serialization classes
    [System.Serializable]
    public class IntersectionMessage
    {
        public string message_type;
        public IntersectionData[] intersections;
    }

    [System.Serializable]
    public class IntersectionData
    {
        public int id;
        public float world_x;
        public float world_y;
        public float world_z;
        public string type;
        public int camera1_x;
        public int camera1_y;
        public int camera2_x;
        public int camera2_y;
    }
}
