using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

namespace TrafficSimulation {
    public class DeleteOffScreen : MonoBehaviour
    {
        public void OnCollisionEnter(Collision collision){

            if (collision.gameObject.tag == "Destructor" ){
                if(this.GetComponent<VehicleAI>().isRobberCar){
                    Debug.Log("ROBBER ESCAPED");
                }
                Destroy(this.gameObject);
            }
        }
    }
}