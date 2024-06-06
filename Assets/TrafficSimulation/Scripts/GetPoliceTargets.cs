using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;


namespace TrafficSimulation{
   public class GetPoliceTargets : MonoBehaviour
   {
       public List<Segment> policeTargets;
       private TrafficSystem trafficSystem;
       public List<Segment> segments;
       public List<Waypoint> waypoints;
       public int deltaThreshold = 1; // sensitivity to minor coordinate fluxuation as predicted direction
       private Segment currentRobberSegment;
       private float closestWaypointDelta = float.MaxValue;
       private Vector3 closestWaypointPosition = new Vector3(float.MaxValue, float.MaxValue, float.MaxValue);


       void Start()
       {
           trafficSystem = GetComponentInParent<TrafficSystem>();
           segments = trafficSystem.segments;
       }


       public List<Segment> setPoliceTargets(Vector3[] robberLoc){
           foreach(Segment segment in segments){
               // Debug.Log("segment " + segment.id);
               waypoints = segment.getWaypoints();


               foreach(Waypoint waypoint in waypoints){
                   Vector3 waypointPosition = Camera.main.WorldToScreenPoint(waypoint.transform.position);
                   // Debug.Log(segment.id + " " + waypoint + " with coordinates: " + waypointPosition);
                   float euclideanDistance = Math.Abs(waypointPosition.x - robberLoc[0].x) + Math.Abs(waypointPosition.z - robberLoc[0].z);
                   // Debug.Log("segment: " + segment);
                   if(euclideanDistance < closestWaypointDelta){
                       // if no direction, return the closest waypoint
                       if(robberLoc[1] == Vector3.zero){
                           setRobberLocation(euclideanDistance, waypointPosition, segment);
                       }
                       // return closest waypoint in direction of travel
                       else{
                           // if robber is moving right and closest waypoint is to the right
                           if(robberLoc[0].x - robberLoc[1].x > deltaThreshold && closestWaypointPosition.x - robberLoc[1].x > 0){
                               setRobberLocation(euclideanDistance, waypointPosition, segment);
                           }
                           // if robber is moving left and closeest waypoint is to the left
                           else if(robberLoc[0].x - robberLoc[1].x < deltaThreshold && closestWaypointPosition.x - robberLoc[1].x < 0){
                               setRobberLocation(euclideanDistance, waypointPosition, segment);
                           }
                           // if robber is moving up and closest waypoint is up
                           else if(robberLoc[0].z - robberLoc[1].z > deltaThreshold && closestWaypointPosition.z - robberLoc[1].z > 0){
                               setRobberLocation(euclideanDistance, waypointPosition, segment);
                           }
                           // if robber is moving down and closest waypoint is down
                           else if(robberLoc[0].z - robberLoc[1].z < deltaThreshold && closestWaypointPosition.z - robberLoc[1].z < 0){
                               setRobberLocation(euclideanDistance, waypointPosition, segment);
                           }
                           // otherwise robber is moving away from this waypoint and it should not be considered closest to the robber
                       }
                   }
               }
           }
           Debug.Log("CURRENT ROBBER SEGMENT ID: " + currentRobberSegment);
           policeTargets = currentRobberSegment.nextSegments;
          
           return policeTargets;
       }


       public void setRobberLocation(float euclideanDistance, Vector3 waypointPosition, Segment segment){
           closestWaypointDelta = euclideanDistance;
           closestWaypointPosition = waypointPosition;
           currentRobberSegment = segment;
           // Debug.Log("updated currentRobberSegment: " + currentRobberSegment);
       }
   }
}
