#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace AegisFlorae.EditorTools
{
    /// <summary>
    /// Import presets and checks for reviewed art staged under Assets/Aegis/Art only.
    /// This tool never scans or changes Unity/Assets/Models or any other project path.
    /// </summary>
    public static class AegisAssetImport
    {
        private const string TextureRoot = "Assets/Aegis/Art/Textures";
        private const string PresetLabel = "AegisArtPipeline";
        private const string MapLabelPrefix = "AegisMap:";

        private enum MapKind
        {
            BaseColor,
            Normal,
            Metallic,
            Roughness,
            Smoothness,
            Occlusion,
            Height,
            EmissionMask,
            Data,
            Unknown
        }

        [MenuItem("Aegis/Art Pipeline/Apply Texture Import Presets")]
        public static void ApplyTextureImportPresets()
        {
            if (!Directory.Exists(ToAbsolutePath(TextureRoot)))
            {
                Debug.LogWarning($"Aegis Art Pipeline: create {TextureRoot} and stage reviewed textures there first.");
                return;
            }

            string[] guids = AssetDatabase.FindAssets("t:Texture2D", new[] { TextureRoot });
            int changed = 0;
            int unrecognized = 0;
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!IsInsideTextureRoot(path)) continue;

                MapKind kind = GetMapKind(Path.GetFileNameWithoutExtension(path));
                if (kind == MapKind.Unknown)
                {
                    unrecognized++;
                    continue;
                }

                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null) continue;

                bool shouldBeNormal = kind == MapKind.Normal;
                bool shouldUseSrgb = kind == MapKind.BaseColor;
                bool changedSettings = importer.textureType != (shouldBeNormal ? TextureImporterType.NormalMap : TextureImporterType.Default)
                    || importer.sRGBTexture != shouldUseSrgb;

                importer.textureType = shouldBeNormal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                importer.sRGBTexture = shouldUseSrgb;
                importer.alphaIsTransparency = shouldUseSrgb && importer.DoesSourceTextureHaveAlpha();

                var labels = new List<string>(importer.GetLabels());
                AddLabel(labels, PresetLabel);
                RemoveMapLabels(labels);
                AddLabel(labels, MapLabelPrefix + kind);
                AddLabel(labels, shouldUseSrgb ? "AegisColorSpace:sRGB" : "AegisColorSpace:Linear");
                importer.SetLabels(labels.ToArray());

                if (changedSettings) changed++;
                EditorUtility.SetDirty(importer);
                importer.SaveAndReimport();
            }

            Debug.Log($"Aegis Art Pipeline: applied/confirmed presets for {guids.Length - unrecognized} recognized textures under {TextureRoot}; {changed} had import settings updated; {unrecognized} had unrecognized suffixes and were left untouched.");
            ValidateArtTextures();
        }

        [MenuItem("Aegis/Art Pipeline/Validate Art Textures")]
        public static void ValidateArtTextures()
        {
            if (!Directory.Exists(ToAbsolutePath(TextureRoot)))
            {
                Debug.LogWarning($"Aegis Art Pipeline: texture root not found: {TextureRoot}");
                return;
            }

            string[] guids = AssetDatabase.FindAssets("t:Texture2D", new[] { TextureRoot });
            var mapsByStem = new Dictionary<string, HashSet<MapKind>>(StringComparer.OrdinalIgnoreCase);
            int errors = 0;
            int warnings = 0;
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!IsInsideTextureRoot(path)) continue;

                string file = Path.GetFileNameWithoutExtension(path);
                MapKind kind = GetMapKind(file);
                if (kind == MapKind.Unknown)
                {
                    Debug.LogWarning($"Aegis Art Pipeline: unknown map suffix; leave untouched or rename with a documented suffix: {path}");
                    warnings++;
                    continue;
                }

                string stem = GetStem(file, kind);
                if (!mapsByStem.TryGetValue(stem, out HashSet<MapKind> maps))
                {
                    maps = new HashSet<MapKind>();
                    mapsByStem.Add(stem, maps);
                }
                if (!maps.Add(kind))
                {
                    Debug.LogError($"Aegis Art Pipeline: more than one {kind} map uses material stem '{stem}'. Check extensions/case: {path}");
                    errors++;
                }

                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null)
                {
                    Debug.LogError($"Aegis Art Pipeline: expected a TextureImporter for {path}");
                    errors++;
                    continue;
                }

                bool shouldBeNormal = kind == MapKind.Normal;
                bool shouldUseSrgb = kind == MapKind.BaseColor;
                if (importer.textureType != (shouldBeNormal ? TextureImporterType.NormalMap : TextureImporterType.Default))
                {
                    Debug.LogError($"Aegis Art Pipeline: wrong texture type for {path}; run Apply Texture Import Presets.");
                    errors++;
                }
                if (importer.sRGBTexture != shouldUseSrgb)
                {
                    Debug.LogError($"Aegis Art Pipeline: wrong sRGB setting for {path}; run Apply Texture Import Presets.");
                    errors++;
                }
                if (!Array.Exists(importer.GetLabels(), label => label == PresetLabel || label.StartsWith(MapLabelPrefix, StringComparison.Ordinal)))
                {
                    Debug.LogWarning($"Aegis Art Pipeline: missing import metadata labels for {path}; run Apply Texture Import Presets.");
                    warnings++;
                }
            }

            foreach (KeyValuePair<string, HashSet<MapKind>> entry in mapsByStem)
            {
                HashSet<MapKind> maps = entry.Value;
                if (!maps.Contains(MapKind.BaseColor))
                {
                    Debug.LogWarning($"Aegis Art Pipeline: '{entry.Key}' has data maps but no _BaseColor/_Albedo map.");
                    warnings++;
                }
                if (maps.Contains(MapKind.Roughness) && maps.Contains(MapKind.Smoothness))
                {
                    Debug.LogError($"Aegis Art Pipeline: '{entry.Key}' contains both _Roughness and _Smoothness. Choose one source convention before packing.");
                    errors++;
                }
            }

            string message = $"Aegis Art Pipeline validation: {guids.Length} textures, {errors} error(s), {warnings} warning(s). Texture suffix validation does not verify license, visual quality, packed URP channels, or provenance.";
            if (errors == 0) Debug.Log(message);
            else Debug.LogError(message);
        }

        private static bool IsInsideTextureRoot(string path)
        {
            return path.StartsWith(TextureRoot + "/", StringComparison.Ordinal)
                && !path.Contains("/../")
                && !path.Contains("\\");
        }

        private static string ToAbsolutePath(string assetPath)
        {
            return Path.GetFullPath(Path.Combine(Application.dataPath, assetPath.Substring("Assets/".Length)));
        }

        private static MapKind GetMapKind(string fileName)
        {
            if (HasSuffix(fileName, "_BaseColor") || HasSuffix(fileName, "_Albedo") || HasSuffix(fileName, "_Color")) return MapKind.BaseColor;
            if (HasSuffix(fileName, "_Normal") || HasSuffix(fileName, "_N")) return MapKind.Normal;
            if (HasSuffix(fileName, "_Metallic")) return MapKind.Metallic;
            if (HasSuffix(fileName, "_Roughness")) return MapKind.Roughness;
            if (HasSuffix(fileName, "_Smoothness")) return MapKind.Smoothness;
            if (HasSuffix(fileName, "_AO") || HasSuffix(fileName, "_Occlusion")) return MapKind.Occlusion;
            if (HasSuffix(fileName, "_Height")) return MapKind.Height;
            if (HasSuffix(fileName, "_EmissionMask")) return MapKind.EmissionMask;
            if (HasSuffix(fileName, "_Data")) return MapKind.Data;
            return MapKind.Unknown;
        }

        private static string GetStem(string fileName, MapKind kind)
        {
            string[] suffixes = kind switch
            {
                MapKind.BaseColor => new[] { "_BaseColor", "_Albedo", "_Color" },
                MapKind.Normal => new[] { "_Normal", "_N" },
                MapKind.Metallic => new[] { "_Metallic" },
                MapKind.Roughness => new[] { "_Roughness" },
                MapKind.Smoothness => new[] { "_Smoothness" },
                MapKind.Occlusion => new[] { "_Occlusion", "_AO" },
                MapKind.Height => new[] { "_Height" },
                MapKind.EmissionMask => new[] { "_EmissionMask" },
                MapKind.Data => new[] { "_Data" },
                _ => Array.Empty<string>()
            };
            foreach (string suffix in suffixes)
                if (HasSuffix(fileName, suffix)) return fileName.Substring(0, fileName.Length - suffix.Length);
            return fileName;
        }

        private static bool HasSuffix(string value, string suffix)
        {
            return value.EndsWith(suffix, StringComparison.OrdinalIgnoreCase);
        }

        private static void AddLabel(List<string> labels, string label)
        {
            if (!labels.Contains(label)) labels.Add(label);
        }

        private static void RemoveMapLabels(List<string> labels)
        {
            labels.RemoveAll(label => label.StartsWith(MapLabelPrefix, StringComparison.Ordinal)
                || label.StartsWith("AegisColorSpace:", StringComparison.Ordinal));
        }
    }
}
#endif
