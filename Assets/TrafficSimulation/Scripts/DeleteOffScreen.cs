using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DeleteOffScreen : MonoBehaviour
{
    public Vector2 widthThresold;
    public Vector2 heightThresold;
    // Start is called before the first frame update
    void Start()
    {
        widthThresold = new Vector2(-0.1f, Screen.width * 1.04f);
        heightThresold = new Vector2(-0.1f, Screen.height * 1.04f);
    }

    // Update is called once per frame
    void Update()
    {
        Vector2 screenPosition = Camera.main.WorldToScreenPoint(transform.position);
        if (screenPosition.x < widthThresold.x || 
            screenPosition.y < 0 ||
            screenPosition.x > widthThresold.y || 
            screenPosition.y > heightThresold.y)
        {
            Destroy(gameObject);
        }
    }
}