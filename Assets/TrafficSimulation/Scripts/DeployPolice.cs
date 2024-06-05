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
                int currentTarget = robberVehicleAI.getCurrentTargetSeg();
                int futureTarget = robberVehicleAI.getFutureTargetSeg();
                // get robber's target's 4 adjacent waypoints
                // update police's destination
                    // update vehicleAI to handle police vehicles and thier directions
                

                return;
            }
        }
    }

}

