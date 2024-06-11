using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting.Dependencies.Sqlite;
using UnityEngine;

namespace TrafficSimulation {
    public struct Target {
        public int segment;
        public int waypoint;
    }

    public enum Status {
        GO,
        STOP,
        SLOW_DOWN
    }

    public class VehicleAI : MonoBehaviour {
        [Header("Traffic System")]
        [Tooltip("Current active traffic system")]
        public TrafficSystem trafficSystem;

        [Tooltip("Determine when the vehicle has reached its target. Can be used to \"anticipate\" earlier the next waypoint (the higher this number is, the earlier it will anticipate the next waypoint)")]
        public float waypointThresh = 2.5f;

        [Header("Radar")]
        [Tooltip("Empty gameobject from where the rays will be casted")]
        public Transform raycastAnchor;

        [Tooltip("Length of the casted rays")]
        public float raycastLength = 4;

        [Tooltip("Spacing between each rays")]
        public int raySpacing = 3;

        [Tooltip("Number of rays to be casted")]
        public int raysNumber = 8;

        [Tooltip("If detected vehicle is below this distance, ego vehicle will stop")]
        public float emergencyBrakeThresh = 1.5f;

        [Tooltip("If detected vehicle is below this distance (and above, above distance), ego vehicle will slow down")]
        public float slowDownThresh = 5f;

        [Tooltip("Toggle to select as robber")]
        public bool isRobberCar = false;

        [Tooltip("Add target escape location for robber vehicles")]
        public GameObject escapeLocation = null;

        [Tooltip("Select as 0, 1, or 2 if police")]
        public Segment policeTarget;

        [Tooltip("Toggle for police")]
        public bool isPolice = false;

        [HideInInspector]
        public Status vehicleStatus = Status.GO;

        private WheelDrive wheelDrive;
        private float initMaxSpeed = 0;
        private int pastTargetSegment = -1;
        private Target currentTarget;
        private Target futureTarget;

        public int getCurrentTargetSeg() {
            return currentTarget.segment;
        }

        public int getFutureTargetSeg() {
            return futureTarget.segment;
        }

        public void setPoliceTarget(Segment target) {
            policeTarget = target;
        }

        void Start() {
            wheelDrive = this.GetComponent<WheelDrive>();

            if (trafficSystem == null)
                return;

            initMaxSpeed = wheelDrive.maxSpeed;
            SetWaypointVehicleIsOn();

            if (isPolice) {
                vehicleStatus = Status.STOP;
            }
        }

        public void setPoliceStatus() {
            vehicleStatus = Status.GO;
        }

        void Update() {
            if (trafficSystem == null)
                return;

            WaypointChecker();
            MoveVehicle();
        }

        public void setTrafficSystem(TrafficSystem trafficSys) {
            trafficSystem = trafficSys;
        }

        public bool IsTurningLeft() {
            Waypoint currentWaypoint = trafficSystem.segments[currentTarget.segment].waypoints[currentTarget.waypoint];
            Waypoint nextWaypoint = trafficSystem.segments[futureTarget.segment].waypoints[futureTarget.waypoint];
            Vector3 direction = nextWaypoint.transform.position - currentWaypoint.transform.position;
            float angle = Vector3.SignedAngle(transform.forward, direction, Vector3.up);
            return angle > 35f && angle < 135f;
        }

        public bool CanTurnLeft() {
            RaycastHit hit;
            if (Physics.Raycast(transform.position, transform.forward, out hit, raycastLength)) {
                if (hit.collider.tag == "AutonomousVehicle") {
                    return false;
                }
            }
            return true;
        }

        void WaypointChecker() {
            GameObject waypoint = trafficSystem.segments[currentTarget.segment].waypoints[currentTarget.waypoint].gameObject;
            Vector3 wpDist = this.transform.InverseTransformPoint(new Vector3(waypoint.transform.position.x, this.transform.position.y, waypoint.transform.position.z));

            if (wpDist.magnitude < waypointThresh) {
                currentTarget.waypoint++;
                if (currentTarget.waypoint >= trafficSystem.segments[currentTarget.segment].waypoints.Count) {
                    // If the police car has reached its target segment, set status to STOP
                    if (isPolice && policeTarget != null && currentTarget.segment == policeTarget.id) {
                        Debug.Log("! In the double if");
                        currentTarget.waypoint--;
                        vehicleStatus = Status.STOP;
                        return;
                    }

                    pastTargetSegment = currentTarget.segment;
                    currentTarget.segment = futureTarget.segment;
                    currentTarget.waypoint = 0;

                    
                }

                futureTarget.waypoint = currentTarget.waypoint + 1;
                if (futureTarget.waypoint >= trafficSystem.segments[currentTarget.segment].waypoints.Count) {
                    futureTarget.waypoint = 0;
                    futureTarget.segment = GetNextSegmentId();
                }
            }
            // else if (isPolice && policeTarget != null && currentTarget.segment == policeTarget.id && vehicleStatus == Status.GO) {
            //     // If the police car has already reached its target, set status to STOP
            //     vehicleStatus = Status.STOP;
            // }
        }

        void MoveVehicle() {
            float acc = 1;
            float brake = 0;
            float steering = 0;
            wheelDrive.maxSpeed = initMaxSpeed;

            Transform targetTransform = trafficSystem.segments[currentTarget.segment].waypoints[currentTarget.waypoint].transform;
            Transform futureTargetTransform = trafficSystem.segments[futureTarget.segment].waypoints[futureTarget.waypoint].transform;
            Vector3 futureVel = futureTargetTransform.position - targetTransform.position;
            float futureSteering = Mathf.Clamp(this.transform.InverseTransformDirection(futureVel.normalized).x, -1, 1);

            if (vehicleStatus == Status.STOP) {
                acc = 0;
                brake = 1;
                wheelDrive.maxSpeed = Mathf.Min(wheelDrive.maxSpeed / 2f, 5f);
            } else {
                if (vehicleStatus == Status.SLOW_DOWN) {
                    acc = .3f;
                    brake = 0f;
                }

                if (futureSteering > .3f || futureSteering < -.3f) {
                    wheelDrive.maxSpeed = Mathf.Min(wheelDrive.maxSpeed, wheelDrive.steeringSpeedMax);
                }

                float hitDist;
                GameObject obstacle = GetDetectedObstacles(out hitDist);

                if (obstacle != null) {
                    WheelDrive otherVehicle = null;
                    otherVehicle = obstacle.GetComponent<WheelDrive>();

                    if (otherVehicle != null) {
                        float dotFront = Vector3.Dot(this.transform.forward, otherVehicle.transform.forward);

                        if (otherVehicle.maxSpeed < wheelDrive.maxSpeed && dotFront > .8f) {
                            float ms = Mathf.Max(wheelDrive.GetSpeedMS(otherVehicle.maxSpeed) - .5f, .1f);
                            wheelDrive.maxSpeed = wheelDrive.GetSpeedUnit(ms);
                        }

                        if (hitDist < emergencyBrakeThresh && dotFront > .8f) {
                            acc = 0;
                            brake = 1;
                            wheelDrive.maxSpeed = Mathf.Max(wheelDrive.maxSpeed / 2f, wheelDrive.minSpeed);
                        } else if (hitDist < emergencyBrakeThresh && dotFront <= .8f) {
                            acc = -.3f;
                            brake = 0f;
                            wheelDrive.maxSpeed = Mathf.Max(wheelDrive.maxSpeed / 2f, wheelDrive.minSpeed);
                            float dotRight = Vector3.Dot(this.transform.forward, otherVehicle.transform.right);
                            if (dotRight > 0.1f) steering = -.3f;
                            else if (dotRight < -0.1f) steering = .3f;
                            else steering = -.7f;
                        } else if (hitDist < slowDownThresh) {
                            acc = .5f;
                            brake = 0f;
                        }
                    } else {
                        if (hitDist < emergencyBrakeThresh) {
                            acc = 0;
                            brake = 1;
                            wheelDrive.maxSpeed = Mathf.Max(wheelDrive.maxSpeed / 2f, wheelDrive.minSpeed);
                        } else if (hitDist < slowDownThresh) {
                            acc = .5f;
                            brake = 0f;
                        }
                    }
                }

                if (acc > 0f) {
                    Vector3 desiredVel = trafficSystem.segments[currentTarget.segment].waypoints[currentTarget.waypoint].transform.position - this.transform.position;
                    steering = Mathf.Clamp(this.transform.InverseTransformDirection(desiredVel.normalized).x, -1f, 1f);
                }
            }

            wheelDrive.Move(acc, steering, brake);
        }

        GameObject GetDetectedObstacles(out float _hitDist) {
            GameObject detectedObstacle = null;
            float minDist = 1000f;

            float initRay = (raysNumber / 2f) * raySpacing;
            float hitDist = -1f;
            for (float a = -initRay; a <= initRay; a += raySpacing) {
                CastRay(raycastAnchor.transform.position, a, this.transform.forward, raycastLength, out detectedObstacle, out hitDist);

                if (detectedObstacle == null) continue;

                float dist = Vector3.Distance(this.transform.position, detectedObstacle.transform.position);
                if (dist < minDist) {
                    minDist = dist;
                    break;
                }
            }

            _hitDist = hitDist;
            return detectedObstacle;
        }

        void CastRay(Vector3 _anchor, float _angle, Vector3 _dir, float _length, out GameObject _outObstacle, out float _outHitDistance) {
            _outObstacle = null;
            _outHitDistance = -1f;

            Debug.DrawRay(_anchor, Quaternion.Euler(0, _angle, 0) * _dir * _length, new Color(1, 0, 0, 0.5f));

            int layer = 1 << LayerMask.NameToLayer("AutonomousVehicle");
            int finalMask = layer;

            foreach (string layerName in trafficSystem.collisionLayers) {
                int id = 1 << LayerMask.NameToLayer(layerName);
                finalMask = finalMask | id;
            }

            RaycastHit hit;
            if (Physics.Raycast(_anchor, Quaternion.Euler(0, _angle, 0) * _dir, out hit, _length, finalMask)) {
                _outObstacle = hit.collider.gameObject;
                _outHitDistance = hit.distance;
            }
        }

        int GetNextSegmentId() {
            List<TrafficSimulation.Segment> nextSegs = trafficSystem.segments[currentTarget.segment].nextSegments;

            if (nextSegs.Count == 0)
                return 0;
            else if (isRobberCar) {
                Vector3 targetLoc = Camera.main.WorldToScreenPoint(escapeLocation.transform.position);

                TrafficSimulation.Segment closestSeg = null;
                float closestSegDist = float.MaxValue;

                foreach (var nextSeg in nextSegs) {
                    Vector3 screenPos = Camera.main.WorldToScreenPoint(nextSeg.waypoints[nextSeg.waypoints.Count - 1].transform.position);
                    float manhattanDist = Math.Abs(screenPos.x - targetLoc.x) + Math.Abs(screenPos.z - targetLoc.z);

                    if (manhattanDist < closestSegDist) {
                        closestSegDist = manhattanDist;
                        closestSeg = nextSeg;
                    }
                }
                return closestSeg.id;
            } else if (isPolice && policeTarget != null) {
                Vector3 targetLoc = Camera.main.WorldToScreenPoint(policeTarget.transform.position);

                TrafficSimulation.Segment closestSeg = null;
                float closestSegDist = float.MaxValue;

                foreach (var nextSeg in nextSegs) {
                    Vector3 screenPos = Camera.main.WorldToScreenPoint(nextSeg.waypoints[nextSeg.waypoints.Count - 1].transform.position);
                    float manhattanDist = Math.Abs(screenPos.x - targetLoc.x) + Math.Abs(screenPos.z - targetLoc.z);

                    if (manhattanDist < closestSegDist) {
                        closestSegDist = manhattanDist;
                        closestSeg = nextSeg;
                    }
                }
                return closestSeg.id;
            } else {
                int c = UnityEngine.Random.Range(0, nextSegs.Count);
                return nextSegs[c].id;
            }
        }

        void SetWaypointVehicleIsOn() {
            foreach (Segment segment in trafficSystem.segments) {
                if (segment.IsOnSegment(this.transform.position)) {
                    currentTarget.segment = segment.id;

                    float minDist = float.MaxValue;
                    for (int j = 0; j < trafficSystem.segments[currentTarget.segment].waypoints.Count; j++) {
                        float d = Vector3.Distance(this.transform.position, trafficSystem.segments[currentTarget.segment].waypoints[j].transform.position);

                        Vector3 lSpace = this.transform.InverseTransformPoint(trafficSystem.segments[currentTarget.segment].waypoints[j].transform.position);
                        if (d < minDist && lSpace.z > 0) {
                            minDist = d;
                            currentTarget.waypoint = j;
                        }
                    }
                    break;
                }
            }

            futureTarget.waypoint = currentTarget.waypoint + 1;
            futureTarget.segment = currentTarget.segment;

            if (futureTarget.waypoint >= trafficSystem.segments[currentTarget.segment].waypoints.Count) {
                futureTarget.waypoint = 0;
                futureTarget.segment = GetNextSegmentId();
            }
        }

        public int GetSegmentVehicleIsIn() {
            int vehicleSegment = currentTarget.segment;
            bool isOnSegment = trafficSystem.segments[vehicleSegment].IsOnSegment(this.transform.position);
            if (!isOnSegment) {
                bool isOnPSegement = trafficSystem.segments[pastTargetSegment].IsOnSegment(this.transform.position);
                if (isOnPSegement)
                    vehicleSegment = pastTargetSegment;
            }
            return vehicleSegment;
        }
        
    }
}
