from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
import time

class CentroidTracker:
    def __init__(self, maxDisappeared=10): # was originally 50
        # initialize the next unique object ID along with two ordered
        # dictionaries used to keep track of mapping a given object
        # ID to its centroid and number of consecutive frames it has
        # been marked as "disappeared", respectively
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()

        # NEW: Track velocities, position history, and timestamps
        self.velocities = OrderedDict()
        self.history = OrderedDict()
        self.timestamps = OrderedDict()
        self.history_length = 5  # Keep last 5 positions

        # store the number of maximum consecutive frames a given
        # object is allowed to be marked as "disappeared" until we
        # need to deregister the object from tracking
        self.maxDisappeared = maxDisappeared

    def register(self, centroid):
        # when registering an object we use the next available object
        # ID to store the centroid
        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0

        # NEW: Initialize velocity and history
        self.velocities[self.nextObjectID] = np.array([0, 0])
        self.history[self.nextObjectID] = [centroid]
        self.timestamps[self.nextObjectID] = time.time()

        self.nextObjectID += 1

    def deregister(self, objectID):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.objects[objectID]
        del self.disappeared[objectID]

        # NEW: Clean up velocity and history
        if objectID in self.velocities:
            del self.velocities[objectID]
        if objectID in self.history:
            del self.history[objectID]
        if objectID in self.timestamps:
            del self.timestamps[objectID]

    def update(self, rects):
        # check to see if the list of input bounding box rectangles
        # is empty
        if len(rects) == 0:
            # loop over any existing tracked objects and mark them
            # as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # return early as there are no centroids or tracking info
            # to update
            return self.objects

        # initialize an array of input centroids for the current frame
        inputCentroids = np.zeros((len(rects), 2), dtype="int")

        # loop over the bounding box rectangles
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            # use the bounding box coordinates to derive the centroid
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)

        # if we are currently not tracking any objects take the input
        # centroids and register each of them
        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i])

        # otherwise, are are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            # grab the set of object IDs and corresponding centroids
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())

            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            D = dist.cdist(np.array(objectCentroids), inputCentroids)

            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value as at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()

            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]

            # in order to determine if we need to update, register,
            # or deregister an object we need to keep track of which
            # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                # val
                if row in usedRows or col in usedCols:
                    continue

                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                objectID = objectIDs[row]
                old_centroid = self.objects[objectID]
                new_centroid = inputCentroids[col]

                self.objects[objectID] = new_centroid
                self.disappeared[objectID] = 0

                # NEW: Calculate velocity and update history
                current_time = time.time()
                dt = current_time - self.timestamps.get(objectID, current_time)

                if dt > 0:
                    # Calculate velocity (pixels per second)
                    velocity = (new_centroid - old_centroid) / dt
                    self.velocities[objectID] = velocity
                else:
                    # First frame or same timestamp
                    self.velocities[objectID] = np.array([0, 0])

                # Update timestamp
                self.timestamps[objectID] = current_time

                # Update position history
                if objectID not in self.history:
                    self.history[objectID] = []
                self.history[objectID].append(new_centroid)
                if len(self.history[objectID]) > self.history_length:
                    self.history[objectID].pop(0)

                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)

            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                for row in unusedRows:
                    # grab the object ID for the corresponding row
                    # index and increment the disappeared counter
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    # check to see if the number of consecutive
                    # frames the object has been marked "disappeared"
                    # for warrants deregistering the object
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            else:
                for col in unusedCols:
                    self.register(inputCentroids[col])

        # return the set of trackable objects
        return self.objects

    def get_velocity(self, objectID):
        """Get velocity vector for an object (pixels per second)"""
        if objectID in self.velocities:
            return self.velocities[objectID]
        return np.array([0, 0])

    def get_speed(self, objectID):
        """Get speed (magnitude of velocity) for an object"""
        velocity = self.get_velocity(objectID)
        return np.linalg.norm(velocity)

    def predict_position(self, objectID, time_ahead):
        """
        Predict future position based on current velocity

        Args:
            objectID: ID of the object to predict
            time_ahead: Time in seconds to predict ahead

        Returns:
            Predicted position as [x, y] or None if object doesn't exist
        """
        if objectID not in self.objects:
            return None

        current_pos = self.objects[objectID]
        velocity = self.get_velocity(objectID)

        # Simple linear prediction: future_pos = current_pos + velocity * time
        predicted_pos = current_pos + (velocity * time_ahead)
        return predicted_pos

    def get_history(self, objectID):
        """Get position history for an object"""
        if objectID in self.history:
            return self.history[objectID]
        return []