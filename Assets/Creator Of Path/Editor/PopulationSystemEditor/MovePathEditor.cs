using UnityEngine;
using System.Collections;
using UnityEditor;

[CustomEditor(typeof(MovePath))]
public class MovePathEditor : Editor {

    public override void OnInspectorGUI()
    {

    }
/*
	public void OnSceneGUI()
	{
		MovePath _MovePath = target as MovePath;

		if(!_MovePath.exit)
		{
			if(Event.current.type == EventType.MouseMove) SceneView.RepaintAll();
 			RaycastHit hit;
			Vector2 mPos = Event.current.mousePosition;
			mPos.y = Screen.height - mPos.y - 40;
			Ray ray = Camera.current.ScreenPointToRay(mPos);

    		if (Physics.Raycast(ray, out hit, 3000)) 
    		{
    			_MovePath.mousePos = hit.point;

    			if((Event.current.type == EventType.mouseDown && Event.current.button == 0))
    			{
    					_MovePath.PointSet(_NewPath.pointLenght, hit.point);
    					_MovePath.pointLenght++;
    			}
        	}
        }
    	if(Event.current.keyCode == (KeyCode.Escape))
    		_MovePath.exit = true;
	}
	*/

}
