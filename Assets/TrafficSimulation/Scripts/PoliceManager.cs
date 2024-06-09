using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Threading;
using System.Linq.Expressions;




namespace TrafficSimulation{
   public class NewBehaviourScript : MonoBehaviour
   {
       public Vector3 robberLoc = Vector3.zero;
       [Tooltip("List police vehicles")]
       public List<GameObject> policeVehicles;
       public GetPoliceTargets getPoliceTargets;
       public List<Segment> policeTargets;
       public GameObject trafficSys;
       private CentroidCoordinate robberCoordinates;
       public int catchingRobberDist = 8;


       void Start()
       {
           getPoliceTargets = GetComponent<GetPoliceTargets>();
           robberCoordinates = GetComponent<CentroidCoordinate>();
       }

       void Update(){
            // check if police is in proximity to robber
            if(robberLoc != Vector3.zero){
               
                foreach (GameObject police in policeVehicles){
                    float euclideanDist = Math.Abs(police.transform.position.x - robberCoordinates.GetReceivedPosition().x) + Math.Abs(police.transform.position.z - robberCoordinates.GetReceivedPosition().z);
                    Debug.Log("euclideanDist: " + euclideanDist + " catching robber dist: " + catchingRobberDist);
                    // if a police car has "caught" the robber by proximity of catchingRobberDist
                    if(euclideanDist < catchingRobberDist){
                        Debug.Log("ROBBER CAUGHT");
                    }
                }
            }

            // if socket recieves new coordinates of robber
            if (robberCoordinates.GetReceivedPosition() != robberLoc){
                Debug.Log("COORDINATES RECIEVED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");

                robberLoc = robberCoordinates.GetReceivedPosition();

                // find robber's current and target segement
                policeTargets = getPoliceTargets.setPoliceTargets(robberLoc);
            
                // copy police and target canidates
                List<Segment> remainingPoliceTargets = new List<Segment>(policeTargets);

                // find closest police car to each point
                foreach (GameObject police in policeVehicles){
                    Vector3 policeLoc = police.transform.position;

                    TrafficSimulation.Segment closestTarget = null;
                    float closestTargetDist = float.MaxValue;

                    // Calculate closest segement to target via euclidean distance
                    foreach(Segment policeTarget in remainingPoliceTargets){
                        // Location of policeTarget's last waypoint's position on screen
                        Vector3 targetLoc = policeTarget.waypoints[policeTarget.waypoints.Count - 1].transform.position;
                        float euclideanDist = Math.Abs(targetLoc.x - policeLoc.x) + Math.Abs(targetLoc.z - policeLoc.z);
                    
                        if(euclideanDist < closestTargetDist){
                            closestTargetDist = euclideanDist;
                            closestTarget = policeTarget;
                        }
                    }

                    // if no more targets remain, dont send an officer
                    if(remainingPoliceTargets.Count == 0){
                        Debug.Log("no targets remaining");
                        break;
                    }

                    // set police car's destination to selected point and set status to go
                    police.GetComponent<VehicleAI>().setPoliceTarget(closestTarget);
                    police.GetComponent<VehicleAI>().setPoliceStatus();
                    Debug.Log("closest target: " + closestTarget);
            
                    remainingPoliceTargets.Remove(closestTarget);
                }
           }
       }
   }
}
