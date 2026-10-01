#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using AegisFlorae;
using AegisFlorae.Slice;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.PackageManager;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using TMPro;

namespace AegisFlorae.Editor
{
    /// <summary>Idempotently creates missing Aegis assets without replacing authored scenes.</summary>
    [InitializeOnLoad]
    public static class AegisProjectInitializer
    {
        public const string BootScenePath = "Assets/Aegis/Scenes/Boot.unity";
        public const string CourtyardScenePath = "Assets/Aegis/Scenes/SanctuaryCourtyard.unity";
        private const string SettingsFolder = "Assets/Aegis/Settings";
        private const string RendererPath = SettingsFolder + "/AegisUniversalRenderer.asset";
        private const string PipelinePath = SettingsFolder + "/AegisUniversalRenderPipeline.asset";

        static AegisProjectInitializer()
        {
            EditorApplication.delayCall += EnsureProject;
        }

        [MenuItem("Aegis/Initialize Project")]
        public static void InitializeProject()
        {
            EnsureProject();
            Debug.Log("Aegis project initialization completed. Existing scenes and settings were preserved.");
        }

        public static void EnsureProject()
        {
            if (EditorApplication.isCompiling || EditorApplication.isPlayingOrWillChangePlaymode)
                return;

            EnsureFolders();
            EnsureTextMeshProResources();
            EnsureRenderingAssets();
            EnsureScene(BootScenePath, CreateBootScene);
            EnsureBootLoader();
            EnsureScene(CourtyardScenePath, CreateCourtyardScene);
            EnsureBuildScenes();
            PlayerSettings.colorSpace = ColorSpace.Linear;
#pragma warning disable 0618 // This named Player setting is still the API used by Unity's Input System package.
            PlayerSettings.SetPropertyInt("activeInputHandler", 2, BuildTargetGroup.Unknown);
#pragma warning restore 0618
            PlayerSettings.companyName = "Aegis Florae";
            PlayerSettings.productName = "Aegis Florae";
            AssetDatabase.SaveAssets();
        }

        private static void EnsureFolders()
        {
            foreach (var folder in new[] { "Assets/Aegis", "Assets/Aegis/Scenes", SettingsFolder })
                if (!AssetDatabase.IsValidFolder(folder))
                {
                    var parent = Path.GetDirectoryName(folder).Replace('\\', '/');
                    var leaf = Path.GetFileName(folder);
                    AssetDatabase.CreateFolder(parent, leaf);
                }
        }

        private static void EnsureRenderingAssets()
        {
            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelinePath);
            if (pipeline == null)
            {
                var renderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(RendererPath);
                if (renderer == null)
                {
                    renderer = ScriptableObject.CreateInstance<UniversalRendererData>();
                    AssetDatabase.CreateAsset(renderer, RendererPath);
                }

                // Public factory in URP 17.3 creates the asset and reloads its built-in resources.
                pipeline = UniversalRenderPipelineAsset.Create(renderer);
                pipeline.name = "Aegis Universal Render Pipeline";
                AssetDatabase.CreateAsset(pipeline, PipelinePath);
            }

            pipeline.supportsHDR = true;
            pipeline.shadowDistance = 110f;
            var pipelineSettings = new SerializedObject(pipeline);
            SetBooleanIfPresent(pipelineSettings, "m_MainLightShadowsSupported", true);
            SetBooleanIfPresent(pipelineSettings, "m_SoftShadowsSupported", true);
            pipelineSettings.ApplyModifiedPropertiesWithoutUndo();
            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;
            IncludeRuntimeShaders();
            EditorUtility.SetDirty(pipeline);
        }

        private static void IncludeRuntimeShaders()
        {
            var graphicsAssets = AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/GraphicsSettings.asset");
            if (graphicsAssets == null || graphicsAssets.Length == 0)
                throw new InvalidOperationException("Unity could not load ProjectSettings/GraphicsSettings.asset.");

            var graphicsSettings = new SerializedObject(graphicsAssets[0]);
            var included = graphicsSettings.FindProperty("m_AlwaysIncludedShaders");
            if (included == null || !included.isArray)
                throw new InvalidOperationException("Unity Graphics Settings has no m_AlwaysIncludedShaders list; required runtime shaders cannot be preserved in player builds.");

            foreach (var shaderName in new[]
                     {
                         "Universal Render Pipeline/Lit",
                         "Universal Render Pipeline/Unlit",
                         "TextMeshPro/Mobile/Distance Field",
                         "UI/Default"
                     })
            {
                var shader = Shader.Find(shaderName);
                if (shader == null)
                    throw new InvalidOperationException("Could not find required runtime shader: " + shaderName + ". Ensure URP and TMP Essential Resources are installed before building.");

                bool present = false;
                for (int i = 0; i < included.arraySize; i++)
                    if (included.GetArrayElementAtIndex(i).objectReferenceValue == shader)
                    {
                        present = true;
                        break;
                    }
                if (!present)
                {
                    included.InsertArrayElementAtIndex(included.arraySize);
                    included.GetArrayElementAtIndex(included.arraySize - 1).objectReferenceValue = shader;
                }
            }
            graphicsSettings.ApplyModifiedPropertiesWithoutUndo();
            AssetDatabase.SaveAssets();
        }

        private static void EnsureTextMeshProResources()
        {
            if (Resources.Load<TMP_Settings>("TMP Settings") != null)
                return;

            var uguiPackage = PackageInfo.FindForAssetPath("Packages/com.unity.ugui/Runtime/TMP/TMP_Settings.cs");
            var packageRoot = uguiPackage != null ? uguiPackage.resolvedPath : null;
            var resourcePackage = string.IsNullOrEmpty(packageRoot)
                ? null
                : Path.Combine(packageRoot, "Package Resources", "TMP Essential Resources.unitypackage");
            if (string.IsNullOrEmpty(resourcePackage) || !File.Exists(resourcePackage))
                throw new InvalidOperationException(
                    "TextMesh Pro Essential Resources are missing. In Unity, use Window > TextMeshPro > Import TMP Essential Resources, then run Aegis > Initialize Project again.");

            AssetDatabase.ImportPackage(resourcePackage, false);
            AssetDatabase.Refresh();
            if (Resources.Load<TMP_Settings>("TMP Settings") == null)
                throw new InvalidOperationException(
                    "TMP Essential Resources import did not create TMP Settings. Use Window > TextMeshPro > Import TMP Essential Resources, then run Aegis > Initialize Project again.");
        }

        private static void SetBooleanIfPresent(SerializedObject serializedObject, string propertyName, bool value)
        {
            var property = serializedObject.FindProperty(propertyName);
            if (property == null || property.propertyType != SerializedPropertyType.Boolean)
                throw new InvalidOperationException("URP no longer exposes the expected serialized boolean " + propertyName + ". Verify the pipeline settings for this Editor version.");
            property.boolValue = value;
        }

        private static void EnsureScene(string path, Action createScene)
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(path) != null)
                return;
            createScene();
        }

        private static void CreateBootScene()
        {
            var scene = CreateAdditiveScene("Boot", out var previousActiveScene);
            var root = new GameObject("Aegis Boot Loader");
            root.AddComponent<AegisBootSceneLoader>();
            EditorSceneManager.SaveScene(scene, BootScenePath);
            CloseCreatedScene(scene, previousActiveScene);
        }

        private static void EnsureBootLoader()
        {
            var scene = SceneManager.GetSceneByPath(BootScenePath);
            var openedHere = !scene.IsValid() || !scene.isLoaded;
            if (openedHere)
                scene = EditorSceneManager.OpenScene(BootScenePath, OpenSceneMode.Additive);

            bool found = false;
            foreach (var root in scene.GetRootGameObjects())
                if (root.GetComponent<AegisBootSceneLoader>() != null)
                {
                    found = true;
                    break;
                }

            if (!found)
            {
                var root = new GameObject("Aegis Boot Loader");
                SceneManager.MoveGameObjectToScene(root, scene);
                root.AddComponent<AegisBootSceneLoader>();
                EditorSceneManager.MarkSceneDirty(scene);
                EditorSceneManager.SaveScene(scene);
            }

            if (openedHere)
                EditorSceneManager.CloseScene(scene, true);
        }

        private static void CreateCourtyardScene()
        {
            var scene = CreateAdditiveScene("SanctuaryCourtyard", out var previousActiveScene);
            var root = new GameObject("Sanctuary Slice");
            root.AddComponent<SanctuarySlice>();
            EditorSceneManager.SaveScene(scene, CourtyardScenePath);
            CloseCreatedScene(scene, previousActiveScene);
        }

        private static Scene CreateAdditiveScene(string sceneName, out Scene previousActiveScene)
        {
            previousActiveScene = SceneManager.GetActiveScene();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
            scene.name = sceneName;
            SceneManager.SetActiveScene(scene);
            return scene;
        }

        private static void CloseCreatedScene(Scene scene, Scene previousActiveScene)
        {
            if (previousActiveScene.IsValid() && previousActiveScene.isLoaded)
                SceneManager.SetActiveScene(previousActiveScene);
            EditorSceneManager.CloseScene(scene, true);
        }

        private static void AddBuildSceneIfMissing(List<EditorBuildSettingsScene> scenes, string path)
        {
            foreach (var scene in scenes)
                if (scene.path == path)
                {
                    scene.enabled = true;
                    return;
                }
            scenes.Add(new EditorBuildSettingsScene(path, true));
        }

        private static void EnsureBuildScenes()
        {
            var current = EditorBuildSettings.scenes;
            var result = new List<EditorBuildSettingsScene>(current);
            AddBuildSceneIfMissing(result, BootScenePath);
            AddBuildSceneIfMissing(result, CourtyardScenePath);
            EditorBuildSettings.scenes = result.ToArray();
        }
    }
}
#endif
