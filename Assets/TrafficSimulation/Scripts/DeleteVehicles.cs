using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

namespace TrafficSimulation {

    public class DeleteOffScreen : MonoBehaviour
    
    {
        public List<GameObject> policeVehicles;
        public GameObject robberEscapedImage = null;
        public void OnCollisionEnter(Collision collision){
        
            if (collision.gameObject.tag == "Destructor" ){
                if(this.GetComponent<VehicleAI>().isRobberCar){
                    robberEscapedImage.SetActive(true);
                    
                    Debug.Log("ROBBER ESCAPED");
                    Debug.Log("Closest police to robber was: " + getClosestPolice() + " units away.");
                }
                Destroy(this.gameObject);
            }
        }

        public float getClosestPolice(){
            float closestPoliceDist = float.MaxValue;

            // Find the police closest to the robber's location
            foreach (GameObject police in policeVehicles) {
                if(police == null){
                    continue;
                }

                float euclideanDist = Vector3.Distance(police.transform.position, this.transform.position);

                if (euclideanDist < closestPoliceDist) {
                    closestPoliceDist = euclideanDist;
                }
            }
            
            return closestPoliceDist;
        }
    }
}