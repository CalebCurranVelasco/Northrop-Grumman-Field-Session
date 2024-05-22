using UnityEngine;
using System.Collections;
using UnityEditor;

public class EditorMenu : Editor {

    [MenuItem("Population System/Create/Walking people")]
    private static void Test2()
    {
        GameObject newPath = new GameObject();
        newPath.name = "New path";
        newPath.AddComponent<NewPath>();
        Selection.activeGameObject = newPath;
    }

	[MenuItem("Population System/Create/Standing people/Audience")]
    private static void Test4()
    {
        var _populationSystemManager = GameObject.Find("Population System").GetComponent<PopulationSystemManager>();
        Selection.activeGameObject = _populationSystemManager.gameObject;
        ActiveEditorTracker.sharedTracker.isLocked = true;
        _populationSystemManager.isConcert = true;
    }

    [MenuItem("Population System/Create/Standing people/Talking people")]
    private static void Test5()
    {
        var _populationSystemManager = GameObject.Find("Population System").GetComponent<PopulationSystemManager>();
        Selection.activeGameObject = _populationSystemManager.gameObject;
        ActiveEditorTracker.sharedTracker.isLocked = true;
        _populationSystemManager.isStreet = true;
    }
}
