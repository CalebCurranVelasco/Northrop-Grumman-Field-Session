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
        public GameObject robberCaughtImage = null;

        private Dictionary<GameObject, Vector3> policeDestinations = new Dictionary<GameObject, Vector3>();

        void Start() {
            getPoliceTargets = GetComponent<GetPoliceTargets>();
            robberCoordinates = GetComponent<Coordinate_Receiver>();
        }

        void Update() {
            // Check if police is in proximity to robber
            if (robberLoc != Vector3.zero) {
                foreach (GameObject police in policeVehicles) {
                    float euclideanDist = Vector3.Distance(police.transform.position, robberCoordinates.GetReceivedPosition());
                    Debug.Log("euclideanDist: " + euclideanDist + " catching robber dist: " + catchingRobberDist);
                    // If a police car has "caught" the robber by proximity of catchingRobberDist
                    if (euclideanDist < catchingRobberDist) {
                        robberCaughtImage.SetActive(true);
                        Debug.Log("ROBBER CAUGHT");
                    }
                }
            }

            // If socket receives new coordinates of robber
            if (robberCoordinates.GetReceivedPosition() != robberLoc) {
                robberLoc = robberCoordinates.GetReceivedPosition();

                // Find robber's current and target segment
                policeTargets = getPoliceTargets.SetPoliceTargets(robberLoc);

                // Copy police and target candidates
                List<Segment> remainingPoliceTargets = new List<Segment>(policeTargets);

                // Ensure there are enough targets to assign
                if (remainingPoliceTargets.Count > 0) {
                    // Assign targets to all police cars, cycling through available segments if necessary
                    for (int i = 0; i < policeVehicles.Count; i++) {
                        GameObject police = policeVehicles[i];
                        int targetIndex = i % remainingPoliceTargets.Count;

                        // Check if police car is not already at its target segment or location
                        if (!policeDestinations.ContainsKey(police) || Vector3.Distance(police.transform.position, policeDestinations[police]) > 1f) {
                            Segment policeTarget = remainingPoliceTargets[targetIndex];
                            Vector3 targetLoc = policeTarget.waypoints[policeTarget.waypoints.Count - 1].transform.position;

                            // Set police car's destination to selected point and set status to go
                            police.GetComponent<VehicleAI>().setPoliceTarget(policeTarget);
                            police.GetComponent<VehicleAI>().setPoliceStatus();
                            Debug.Log("Assigning target to police: " + policeTarget);

                            policeDestinations[police] = targetLoc;
                        }
                    }
                } else {
                    Debug.Log("No targets available for assignment");
                }
            }
        }
    }
}
