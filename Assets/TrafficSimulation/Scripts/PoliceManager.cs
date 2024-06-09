using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

namespace TrafficSimulation {
    public class NewBehaviourScript : MonoBehaviour {
        public Vector3 robberLoc = Vector3.zero;
        [Tooltip("List police vehicles")]
        public List<GameObject> policeVehicles;
        public GetPoliceTargets getPoliceTargets;
        public List<Segment> policeTargets;
        public GameObject trafficSys;
        private Coordinate_Receiver robberCoordinates;
        public int catchingRobberDist = 8;
        private Dictionary<GameObject, Vector3> policeDestinations = new Dictionary<GameObject, Vector3>();

        void Start() {
            getPoliceTargets = GetComponent<GetPoliceTargets>();
            robberCoordinates = GetComponent<Coordinate_Receiver>();
        }

        void Update() {
            // Check if police is in proximity to robber
            if (robberLoc != Vector3.zero) {
                foreach (GameObject police in policeVehicles) {
                    float euclideanDist = Math.Abs(police.transform.position.x - robberCoordinates.GetReceivedPosition().x) + Math.Abs(police.transform.position.z - robberCoordinates.GetReceivedPosition().z);
                    Debug.Log("euclideanDist: " + euclideanDist + " catching robber dist: " + catchingRobberDist);
                    // If a police car has "caught" the robber by proximity of catchingRobberDist
                    if (euclideanDist < catchingRobberDist) {
                        Debug.Log("ROBBER CAUGHT");
                    }
                }
            }

            // If socket receives new coordinates of robber
            if (robberCoordinates.GetReceivedPosition() != robberLoc) {
                Debug.Log("XXX COORDINATES RECEIVED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
                robberLoc = robberCoordinates.GetReceivedPosition();

                // Find robber's current and target segment
                policeTargets = getPoliceTargets.setPoliceTargets(robberLoc);

                // Copy police and target candidates
                List<Segment> remainingPoliceTargets = new List<Segment>(policeTargets);

                // Find closest police car to each point
                foreach (GameObject police in policeVehicles) {
                    // Check if police car is not already at its target segment or location
                    if (!policeDestinations.ContainsKey(police) || Vector3.Distance(police.transform.position, policeDestinations[police]) > 1f) {
                        Vector3 policeLoc = police.transform.position;

                        TrafficSimulation.Segment closestTarget = null;
                        float closestTargetDist = float.MaxValue;

                        // Calculate closest segment to target via euclidean distance
                        foreach (Segment policeTarget in remainingPoliceTargets) {
                            // Location of policeTarget's last waypoint's position on screen
                            Vector3 targetLoc = policeTarget.waypoints[policeTarget.waypoints.Count - 1].transform.position;
                            float euclideanDist = Math.Abs(targetLoc.x - policeLoc.x) + Math.Abs(targetLoc.z - policeLoc.z);

                            if (euclideanDist < closestTargetDist) {
                                closestTargetDist = euclideanDist;
                                closestTarget = policeTarget;
                            }
                        }

                        // If no more targets remain, don't send an officer
                        if (remainingPoliceTargets.Count == 0) {
                            Debug.Log("No targets remaining");
                            break;
                        }

                        // Set police car's destination to selected point and set status to go
                        police.GetComponent<VehicleAI>().setPoliceTarget(closestTarget);
                        police.GetComponent<VehicleAI>().setPoliceStatus();
                        Debug.Log("Closest target: " + closestTarget);

                        policeDestinations[police] = closestTarget.waypoints[closestTarget.waypoints.Count - 1].transform.position;
                        remainingPoliceTargets.Remove(closestTarget);
                    }
                }
            }
        }
    }
}
