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


       public List<Segment> setPoliceTargets(Vector3 robberLoc){
           foreach(Segment segment in segments){
                waypoints = segment.getWaypoints();

               foreach(Waypoint waypoint in waypoints){
                   Vector3 waypointPosition = waypoint.transform.position;
                   float euclideanDistance = Math.Abs(waypointPosition.x - robberLoc.x) + Math.Abs(waypointPosition.z - robberLoc.z);

                   if(euclideanDistance < closestWaypointDelta){
                        setRobberLocation(euclideanDistance, waypointPosition, segment);
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
       }
   }
}
