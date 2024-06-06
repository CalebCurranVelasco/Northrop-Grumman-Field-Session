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

        void Start()
        {
            getPoliceTargets = GetComponent<GetPoliceTargets>();
            trafficSystem = GetComponent<TrafficSystem>();
        }

        void Update()
        {
            // socket listens for robber position

            // if socket recieves coordinates of robber
            if (robberLoc[0] != Vector3.zero){
                // find robber's current and target segement
                policeTargets = getPoliceTargets.setPoliceTargets(robberLoc);

                // copy police and target canidates
                List<GameObject> remainingPoliceVehicles = policeVehicles;
                List<Segment> remainingPoliceTargets = policeTargets;

                // find closest police car to each point
                float minDist = float.MaxValue;
                foreach (GameObject police in remainingPoliceVehicles){
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
                    // set police car's destination to selected point

                    // set the police car's traffic system to activate vehicle
                    police.GetComponent<VehicleAI>().setTrafficSystem(trafficSystem);
                }
            }
        }
    }
}
