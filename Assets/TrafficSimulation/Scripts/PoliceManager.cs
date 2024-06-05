using System.Collections;
using System.Collections.Generic;
using UnityEngine;


namespace TrafficSimulation{
    public class NewBehaviourScript : MonoBehaviour
    {
        public Vector3[] robberLoc = {Vector3.zero, Vector3.zero};
        [Tooltip("List police vehicles")]
        public List<GameObject> policeVehicles;
        public GetPoliceTargets getPoliceTargets;
        public List<Vector3> policeTargets;
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
                // policeTargets = getPoliceTargets.setPoliceTargets(robberLoc);
        
                float minDist = float.MaxValue;
                foreach (GameObject police in policeVehicles){
                    foreach(Vector3 policeTarget in policeTargets){
                        // Vector3 escapeLocPos = Camera.main.WorldToScreenPoint(escapeLocation.transform.position);

                        // TrafficSimulation.Segment closestSeg = null;
                        // float closestSegDist = float.MaxValue;

                        // // Calculate closest segement to target via manhattan distance
                        // foreach(var nextSeg in nextSegs){
                        //     // Location of nextSeg's last waypoint's position on screen
                        //     Vector3 screenPos = Camera.main.WorldToScreenPoint(nextSeg.waypoints[nextSeg.waypoints.Count - 1].transform.position);
                        //     float manhattanDist = Math.Abs(screenPos.x - escapeLocPos.x) + Math.Abs(screenPos.z - escapeLocPos.z);
                        
                        // if(manhattanDist < closestSegDist){
                        //         closestSegDist = manhattanDist;
                        //         closestSeg = nextSeg;
                        //     }
                        // }
                    }


                    // set the police car's traffic system to activate vehicle
                    police.GetComponent<VehicleAI>().setTrafficSystem(trafficSystem);
                }
            }
        }
    }
}
