using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class DeleteRobber : MonoBehaviour
{
    public void OnCollisionEnter(Collision collision){
        if (collision.gameObject.tag == "DestructorRobber" ){
            Debug.Log("collision with cone");
            Destroy(this.gameObject);
        }
        Debug.Log("collision");
    }
}