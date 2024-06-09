using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace TrafficSimulation {
    public class GetPoliceTargets : MonoBehaviour {
        public List<Segment> policeTargets;
        private TrafficSystem trafficSystem;
        public List<Segment> segments;
        public List<Waypoint> waypoints;
        public int deltaThreshold = 1; // sensitivity to minor coordinate fluctuation as predicted direction
        private Segment currentRobberSegment;
        private float closestWaypointDelta = float.MaxValue;

        void Start() {
            trafficSystem = GetComponentInParent<TrafficSystem>();
            segments = trafficSystem.segments;
        }

        public List<Segment> SetPoliceTargets(Vector3 robberLoc) {
            closestWaypointDelta = float.MaxValue;
            currentRobberSegment = null;

            // Find the segment closest to the robber's location
            foreach (Segment segment in segments) {
                waypoints = segment.getWaypoints();

                foreach (Waypoint waypoint in waypoints) {
                    Vector3 waypointPosition = waypoint.transform.position;
                    float euclideanDistance = Vector3.Distance(waypointPosition, robberLoc);

                    if (euclideanDistance < closestWaypointDelta) {
                        closestWaypointDelta = euclideanDistance;
                        currentRobberSegment = segment;
                    }
                }
            }

            // Check if a segment containing the robber's waypoint is found
            if (currentRobberSegment != null) {
                // Add all next segments of the current segment to police targets
                policeTargets = new List<Segment>(currentRobberSegment.nextSegments);
            } else {
                // If the segment containing the robber's waypoint is not found, return an empty list
                policeTargets = new List<Segment>();
            }

            return policeTargets;
        }
    }
}
