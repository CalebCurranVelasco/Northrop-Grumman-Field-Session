using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class DeleteOffScreen : MonoBehaviour
{
    public void OnCollisionEnter(Collision collision){
        if (collision.gameObject.tag == "Destructor" ){
            Destroy(this.gameObject);
        }
    }
}