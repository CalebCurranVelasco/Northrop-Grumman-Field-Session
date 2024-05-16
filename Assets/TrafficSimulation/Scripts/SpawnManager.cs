using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SpawnManager : MonoBehaviour
{
    public GameObject[] cars = new GameObject[3];
    public float targetTime = 0.0f;

    // Update is called once per frame
    void Update()
    {
        targetTime -= Time.deltaTime;        

        if(targetTime <= 0){
            targetTime = Random.Range(3, 8); // set new timer for 1 to 3 sec

            GameObject newCarGameObject = Instantiate(cars[Random.Range(0, cars.Length)], transform.position, Quaternion.identity);
            newCarGameObject.transform.Rotate(1, -90, 1);
            
            Rigidbody newCar = newCarGameObject.GetComponent<Rigidbody>();
            //newCar.AddForce(newCarGameObject.transform.forward * 100f);
        }
    }
}
