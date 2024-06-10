using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

namespace TrafficSimulation {

    public class DeleteOffScreen : MonoBehaviour
    
    {
        public GameObject robberEscapedImage = null;
        public void OnCollisionEnter(Collision collision){
        
            if (collision.gameObject.tag == "Destructor" ){
                if(this.GetComponent<VehicleAI>().isRobberCar){
                    robberEscapedImage.SetActive(true);
                    Debug.Log("ROBBER ESCAPED");
                }
                Destroy(this.gameObject);
            }
        }
    }
}