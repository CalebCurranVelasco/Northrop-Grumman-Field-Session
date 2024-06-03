using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class DeleteRobber : MonoBehaviour
{
    public void OnCollisionEnter(Collision collision){
        if (collision.gameObject.tag == "DestructorRobber" ){
            Destroy(this.gameObject);
        }
    }
}