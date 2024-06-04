using System.Collections;
using System.Collections.Generic;
using TrafficSimulation;
using UnityEngine;

public class SpawnManagerDown : MonoBehaviour
{
    public GameObject[] carPrefabs = new GameObject[3];
    public float targetTime = 0.0f;
    public GameObject trafficSys;

    // Update is called once per frame
    void Update()
    {
        targetTime -= Time.deltaTime;        

        if(targetTime <= 0){
            targetTime = Random.Range(10, 16); // set new timer for 10 to 16 sec

            GameObject newCarGameObject = Instantiate(carPrefabs[Random.Range(0, carPrefabs.Length)], transform.position, Quaternion.identity);
            newCarGameObject.transform.Rotate(1, 1, 1);
            
            Rigidbody newCar = newCarGameObject.GetComponent<Rigidbody>(); // do i need this line?

            //set the TrafficSystem in VehicleAI to 
            trafficSys = GameObject.Find("Traffic System");
            TrafficSystem trafficSystemComponent = trafficSys.GetComponent<TrafficSystem>();
            newCarGameObject.GetComponent<VehicleAI>().setTrafficSystem(trafficSystemComponent);
        }
    }
}
