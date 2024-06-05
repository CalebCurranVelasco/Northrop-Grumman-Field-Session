using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TrafficSimulation;

public class SpawnPolice : MonoBehaviour
{
    public GameObject policePrefab = null;
    public float targetTime = 0.0f;
    public GameObject trafficSys;
    public int nextPoliceID = 0;
    public int policeNeeded = 0;
    

    public SpawnPolice(){
        targetTime -= Time.deltaTime;        

        // if there are still police left to spawn 
        if(policeNeeded > 0 && targetTime <= 0){
            targetTime = 2.0f; // set new timer for 2 sec

            GameObject newPoliceCar = Instantiate(policePrefab, transform.position, Quaternion.identity);
            newPoliceCar.transform.Rotate(1, 90, 1);
            
            //Rigidbody newCar = newPoliceCar.GetComponent<Rigidbody>(); // do i need this line?

            // set the TrafficSystem in VehicleAI to Traffic System
            trafficSys = GameObject.Find("Traffic System");
            TrafficSystem trafficSystemComponent = trafficSys.GetComponent<TrafficSystem>();
            newPoliceCar.GetComponent<VehicleAI>().setTrafficSystem(trafficSystemComponent);

            // set police id
            newPoliceCar.GetComponent<VehicleAI>().policeID = nextPoliceID;
            nextPoliceID ++;
        }
    }
}
