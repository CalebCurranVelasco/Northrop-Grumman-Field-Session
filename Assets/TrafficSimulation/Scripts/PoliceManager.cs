using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class NewBehaviourScript : MonoBehaviour
{
    public Vector3[] robberLoc = {Vector3.zero, Vector3.zero};

    void Start()
    {
        GetPoliceTargets getPoliceTargets = GetComponent<GetPoliceTargets>();
    }

    void Update()
    {
        // socket listens for robber position

        // if socket recieves coordinates of robber
        if (robberLoc[0] != Vector3.zero){
            // find robber's current and target segement
            getPoliceTargets.setPoliceTargets(robberLoc);
            // spawn police
        }
    }
}
