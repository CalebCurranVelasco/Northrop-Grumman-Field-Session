using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DeployPolice : MonoBehaviour
{
    public int[] robberLoc = {-1, -1};
    public int[] policeTargets;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        // if socket gives coordinates for robber
        if (robberLoc[0] != -1 && robberLoc[1] != -1){
            // find robber's target segement 
            // get robber's target's 4 adjacent waypoints
            // update police's destination
                // update vehicleAI to handle police vehicles and thier directions
            

            return;
        }
    }
}
