using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace TrafficSimulation{
    public class DeployPolice : MonoBehaviour
        {
        public Vector3[] robberLoc = {Vector3.zero, Vector3.zero};
        public Vector3[] policeTargets;

        private TrafficSystem trafficSystem; 
        public List<Segment> segments;
        public List<Waypoint> waypoints;
        public int deltaThreshold = 1; // sensitivity to positional change as predicted direction
        void Start()
        {
            trafficSystem = GetComponent<TrafficSystem>();
            segments = trafficSystem.getSegments();

        }

        // Update is called once per frame
        void Update()
        {
            // socket listens for robber position

            // if socket recieves coordinates of robber
            if (robberLoc[0] != Vector3.zero){
                // find robber's current and target segement
                getRobberTargetWaypoint();
            }
        }

        Vector3 getRobberTargetWaypoint()
        {
            float closestWaypointDelta = float.MaxValue;
            Vector3 closestWaypointPosition = new Vector3(float.MaxValue, float.MaxValue, float.MaxValue);

            foreach(Segment segment in segments){
                waypoints = segment.getWaypoints();

                foreach(Waypoint waypoint in waypoints){
                    Vector3 waypointPosition = Camera.main.WorldToScreenPoint(waypoint.transform.position);

                    float euclideanDistance = Math.Abs(waypointPosition.x - robberLoc[0].x) + Math.Abs(waypointPosition.z - robberLoc[0].z);

                    if(euclideanDistance < closestWaypointDelta){
                        if(robberLoc[1] == Vector3.zero){ // if no direction, return the closest 