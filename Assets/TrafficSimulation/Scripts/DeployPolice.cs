using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace TrafficSimulation{
    public class DeployPolice : MonoBehaviour
        {
        // [Tooltip("Add robber vehicle to search for")]
        // public GameObject robberVehicle; 
        public Vector3[] robberLoc = {Vector3.zero, Vector3.zero};
        public Vector3[] policeTargets;

        private TrafficSystem trafficSystem; 
        public List<Segment> segments;
        void Start()
        {
            trafficSystem = GetComponent<TrafficSystem>();
            // segments = trafficSystem.getSegments();
        }

        // Update is called once per frame
        void Update()
        {
            // socket listens for robber position

            // if socket recieves coordinates of robber
            if (robberLoc[0] != Vector3.zero){
                // find robber's current and target segement
                // getRobberTargetWaypoint();
            }
        }

        // Vector3 getRobberTargetWaypoint()
        // {
        //     Vector3 closestWaypointDist  = float.MaxValue;
        //     Vector3 closestWaypoint; 

        //     // foreach(Segment segment in segments){
        //     //     foreach(Waypoint waypoint in segments[segment].waypoints){
        //     //         Vector3 waypointLoc = Camera.main.WorldToScreenPoint(waypoint.transform.position);

        //     //         if(robberLoc[1] == Vector3.zero){ // if no direction, return the closest waypoint
        //     //             float manhattanDist = Math.Abs(waypointLoc.x - robberLoc[0].x) + Math.Abs(waypointLoc.z - robberLoc[0].z);

        //     //             if(manhattanDist < closestWaypointDist){
        //     //                 closestWaypointDist = manhattanDist;
        //     //                 closestWaypointLoc = waypointLoc;
        //     //             } 
        //     //         } else{ // return closest waypoint in direction of travel

        //     //         }
        //     //     }
        //     // }
        //     return closestWaypointDist;
        // }
    }
}

