using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Threading;




namespace TrafficSimulation{
   public class NewBehaviourScript : MonoBehaviour
   {
       public Vector3[] robberLoc = {Vector3.zero, Vector3.zero};
       [Tooltip("List police vehicles")]
       public List<GameObject> policeVehicles;
       public GetPoliceTargets getPoliceTargets;
       public List<Segment> policeTargets;
       public GameObject trafficSys;
       private CentroidCoordinate robberCoordinates;
       public bool doStuff = true;


       void Start()
       {
           getPoliceTargets = GetComponent<GetPoliceTargets>();
        //    trafficSystem = GetComponent<TrafficSystem>();
           robberCoordinates = GetComponent<CentroidCoordinate>();
       }


       void Update()
       {
           // for testing purposes without the socket
           // if socket recieves new coordinates of robber
           // if (robberCoordinates.GetReceivedPosition() != robberLoc[0]){
           //     // update position history
           //     robberLoc[1] = robberLoc[0];
           //     robberLoc[0] = robberCoordinates.GetReceivedPosition();
           if (doStuff){
                doStuff = false;

               // update position history
            //    robberLoc[1] = robberLoc[0];
               robberLoc[0] = new Vector3(-122.62f, 0.07f, 48.00f);
            //    robberLoc[0] = new Vector3(-122.63f, 0.07f, 49.73f); // for testing


               // find robber's current and target segement
               policeTargets = getPoliceTargets.setPoliceTargets(robberLoc);
               
            //    Debug.Log("TARGETS:");
            //    foreach( Segment target in policeTargets){
            //         Debug.Log(target);
            //    }
            
               // copy police and target canidates
                List<Segment> remainingPoliceTargets = policeTargets;
                // int count = 0;

                // find closest police car to each point
                foreach (GameObject police in policeVehicles){
                    // Debug.Log("police number" + count);
                    // count ++;
                    // Debug.Log("**************" + police);
                    Vector3 policeLoc = police.transform.position;

                    TrafficSimulation.Segment closestTarget = null;
                    float closestTargetDist = float.MaxValue;

                    // Calculate closest segement to target via euclidean distance
                    foreach(Segment policeTarget in remainingPoliceTargets){
                        // Location of policeTarget's last waypoint's position on screen
                        Vector3 targetLoc = policeTarget.waypoints[policeTarget.waypoints.Count - 1].transform.position;
                        float euclideanDist = Math.Abs(targetLoc.x - policeLoc.x) + Math.Abs(targetLoc.z - policeLoc.z);
                    
                        if(euclideanDist < closestTargetDist){
                            closestTargetDist = euclideanDist;
                            closestTarget = policeTarget;
                            // Debug.Log("closest target updated to: " + closestTarget);
                        }
                    }
                    // set police car's destination to selected point and traffic system to activate vehicle
                    trafficSys = GameObject.Find("Traffic System");
                    TrafficSystem trafficSystemComponent = trafficSys.GetComponent<TrafficSystem>();
                    police.GetComponent<VehicleAI>().setTrafficSystem(trafficSystemComponent);

                    Debug.Log("closest target: " + closestTarget);
                    police.GetComponent<VehicleAI>().setPoliceTarget(closestTarget);
                
                    // Debug.Log("police.GetComponent<VehicleAI>().policeTarget: " + police.GetComponent<VehicleAI>().policeTarget);

                    remainingPoliceTargets.Remove(closestTarget);
                }
           }
       }
   }
}
