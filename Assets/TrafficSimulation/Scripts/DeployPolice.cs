using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace TrafficSimulation{
    public class DeployPolice : MonoBehaviour
        {
        public VehicleAI robberVehicleAI; // Reference to a VehicleAI instance
        [Tooltip("Add robber vehicle to search for")]
        public GameObject robberVehicle; 
        public Vector3 robberLoc = Vector3.zero;
        public Vector3[] policeTargets;

        private TrafficSystem trafficSystem; 
        public List<Segment> segments;
        void Start()
        {
            // Example of finding the VehicleAI component on the same GameObject
            robberVehicleAI = robberVehicle.GetComponent<VehicleAI>();
        }

        // Update is called once per frame
        void Update()
        {
            // socket listens for robber position

            // if socket recieves coordinates of robber
            if (robberLoc != Vector3.zero){
                // find robber's current and target segement
                trafficSystem = GetComponent<TrafficSystem>();
                segments = trafficSystem.getSegments();

                foreach(Segment segment in segments){
                    //Find nearest waypoint 
                    float closestWaypoint  = float.MaxValue;

                    foreach(Waypoint waypoint in segments[segment].waypoints){
                        Vector3 waypointLoc = Camera.main.WorldToScreenPoint(waypoint.transform.position);
                        
                        if(manhattanDist < closestSegDist){
                            closestSegDist = manhattanDist;
                            closestSeg = nextSeg;
                        }
            


                        float d = Vector3.Distance(this.transform.position, trafficSystem.segments[currentTarget.segment].waypoints[j].transform.position);
                        //Only take in front points
                        Vector3 lSpace = this.transform.InverseTransformPoint(trafficSystem.segments[currentTarget.segment].waypoints[j].transform.position);
                        if(d < minDist && lSpace.z > 0){
                            minDist = d;
                            currentTarget.waypoint = j;
                        }
                    }
                }                
            }
        }
    }
}

