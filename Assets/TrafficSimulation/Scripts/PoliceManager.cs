using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;




namespace TrafficSimulation{
   public class NewBehaviourScript : MonoBehaviour
   {
       public Vector3[] robberLoc = {Vector3.zero, Vector3.zero};
       [Tooltip("List police vehicles")]
       public List<GameObject> policeVehicles;
       public GetPoliceTargets getPoliceTargets;
       public List<Segment> policeTargets;
       public TrafficSystem trafficSystem;
       private CentroidCoordinate robberCoordinates;


       void Start()
       {
           getPoliceTargets = GetComponent<GetPoliceTargets>();
           trafficSystem = GetComponent<TrafficSystem>();
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
           if (true){
               // update position history
               robberLoc[1] = robberLoc[0];
               robberLoc[0] = new Vector3(-59.3f, 0.2f, -80.2f);


               // find robber's current and target segement
               policeTargets = getPoliceTargets.setPoliceTargets(robberLoc);


               // copy police and target canidates
               List<Segment> remainingPoliceTargets = policeTargets;


               // find closest police car to each point
               foreach (GameObject police in policeVehicles){
                   Vector3 policeLoc = Camera.main.WorldToScreenPoint(police.transform.position);


                   TrafficSimulation.Segment closestTarget = null;
                   float closestTargetDist = float.MaxValue;


                   // Calculate closest segement to target via euclidean distance
                   foreach(Segment policeTarget in remainingPoliceTargets){
                       // Location of policeTarget's last waypoint's position on screen
                       Vector3 targetLoc = Camera.main.WorldToScreenPoint(policeTarget.waypoints[policeTarget.waypoints.Count - 1].transform.position);
                       float euclideanDist = Math.Abs(targetLoc.x - policeLoc.x) + Math.Abs(targetLoc.z - policeLoc.z);
                  
                       if(euclideanDist < closestTargetDist){
                           closestTargetDist = euclideanDist;
                           closestTarget = policeTarget;
                       }
                   }
                   // set police car's destination to selected point and traffic system to activate vehicle
                   police.GetComponent<VehicleAI>().policeTarget = closestTarget;
                   police.GetComponent<VehicleAI>().setTrafficSystem(trafficSystem);


                   remainingPoliceTargets.Remove(closestTarget);
               }
           }
       }
   }
}
