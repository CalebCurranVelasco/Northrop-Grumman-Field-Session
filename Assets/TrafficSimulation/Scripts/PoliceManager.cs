using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Threading;




namespace TrafficSimulation{
   public class NewBehaviourScript : MonoBehaviour
   {
       public Vector3 robberLoc = Vector3.zero;
       [Tooltip("List police vehicles")]
       public List<GameObject> policeVehicles;
       public GetPoliceTargets getPoliceTargets;
       public List<Segment> policeTargets;
       public GameObject trafficSys;
       private CentroidCoordinate robberCoordinates;


       void Start()
       {
           getPoliceTargets = GetComponent<GetPoliceTargets>();
        //    trafficSystem = GetComponent<TrafficSystem>();
           robberCoordinates = GetComponent<CentroidCoordinate>();
       }


       void Update(){
        
            // for testing purposes without the socket
            // if socket recieves new coordinates of robber
            // if (robberCoordinates.GetReceivedPosition() != robberLoc){
            // robberLoc = robberCoordinates.GetReceivedPosition();
           
            if(true){
                robberLoc = new Vector3(-124.04f, 0.07f, 49.57f);

                // find robber's current and target segement
                policeTargets = getPoliceTargets.setPoliceTargets(robberLoc);
            
                // copy police and target canidates
                List<Segment> remainingPoliceTargets = new List<Segment>(policeTargets);

                // find closest police car to each point
                foreach (GameObject police in policeVehicles){
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
                    // set police car's destination to selected point and set status to go
                    police.GetComponent<VehicleAI>().setPoliceTarget(closestTarget);
                    police.GetComponent<VehicleAI>().setPoliceStatus();
                    // Debug.Log("closest target: " + closestTarget);
            
                    remainingPoliceTargets.Remove(closestTarget);
                }
           }
       }
   }
}
