#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace AegisFlorae.Editor
{
    public static class AegisBuildCommand
    {
        [MenuItem("Aegis/Build/Windows x64")]
        public static void BuildWindows() => Build(BuildTarget.StandaloneWindows64, "Builds/Windows/AegisFlorae.exe");

        [MenuItem("Aegis/Build/Linux x64")]
        public static void BuildLinux() => Build(BuildTarget.StandaloneLinux64, "Builds/Linux/AegisFlorae.x86_64");

        private static void Build(BuildTarget target, string output)
        {
            AegisProjectInitializer.EnsureProject();
            var root = Directory.GetParent(Application.dataPath).FullName;
            var outputPath = Path.Combine(root, output);
            Directory.CreateDirectory(Path.GetDirectoryName(outputPath));

            var options = new BuildPlayerOptions
            {
                scenes = new[]
                {
                    AegisProjectInitializer.BootScenePath,
                    AegisProjectInitializer.CourtyardScenePath
                },
                locationPathName = outputPath,
                target = target,
                options = BuildOptions.None
            };
            var report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
                throw new System.Exception($"Aegis {target} build failed: {report.summary.result} ({report.summary.totalErrors} errors).");
            Debug.Log($"Aegis {target} build succeeded: {outputPath} ({report.summary.totalSize} bytes).");
        }
    }
}
#endif
