using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace AegisFlorae.Slice
{
    // Locally authored stand-ins: these are NOT generated Meshy or downloaded Poliigon assets.
    // Geometry keeps moving parts separate so accepted production prefabs can replace it.
    public sealed class SliceArtFactory
    {
        public sealed class TowerView
        {
            public Transform Root;
            public Transform Turret;
            public Transform Barrels;
            public Transform Muzzle;
        }

        public readonly Material Stone, StoneDark, Brass, Iron, Teal, Amber, Leaf, Pink, Gold;
        private readonly List<Material> ownedMaterials = new List<Material>();

        public SliceArtFactory()
        {
            Stone = Material("Warm limestone", new Color(.72f, .67f, .53f), 0, .28f);
            StoneDark = Material("Weathered stone", new Color(.41f, .43f, .36f), 0, .16f);
            Brass = Material("Antique brass", new Color(.65f, .43f, .14f), .8f, .55f);
            Iron = Material("Dark cast iron", new Color(.075f, .11f, .12f), .7f, .32f);
            Teal = Material("Aether cyan", new Color(.06f, .8f, .73f), .15f, .65f, 1.6f);
            Amber = Material("Amber optics", new Color(1f, .5f, .06f), .2f, .6f, 1.2f);
            Leaf = Material("Deep verdant foliage", new Color(.065f, .17f, .12f), 0, .18f);
            Pink = Material("Peony petals", new Color(.85f, .38f, .42f), 0, .15f);
            Gold = Material("Chrysanthemum petals", new Color(.92f, .55f, .1f), 0, .2f);
        }

        private Material Material(string name, Color color, float metallic, float smoothness, float glow = 0)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) shader = Shader.Find("Standard");
            if (shader == null) throw new System.InvalidOperationException("No supported surface shader found.");
            var material = new Material(shader) { name = name };
            material.SetColor("_BaseColor", color);
            material.SetColor("_Color", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            if (glow > 0)
            {
                material.EnableKeyword("_EMISSION");
                material.SetColor("_EmissionColor", color * glow);
            }
            ownedMaterials.Add(material);
            return material;
        }

        public static Transform Group(string name, Transform parent, Vector3 position)
        {
            var result = new GameObject(name).transform;
            result.SetParent(parent, false);
            result.localPosition = position;
            return result;
        }

        private static Transform Shape(PrimitiveType primitive, string name, Transform parent,
            Vector3 position, Vector3 scale, Material material, Quaternion? rotation = null)
        {
            GameObject item = GameObject.CreatePrimitive(primitive);
            item.name = name;
            item.transform.SetParent(parent, false);
            item.transform.localPosition = position;
            item.transform.localScale = scale;
            item.transform.localRotation = rotation ?? Quaternion.identity;
            Object.Destroy(item.GetComponent<Collider>());
            item.GetComponent<Renderer>().sharedMaterial = material;
            return item.transform;
        }

        private static Transform Box(string name, Transform parent, Vector3 position, Vector3 scale, Material material)
            => Shape(PrimitiveType.Cube, name, parent, position, scale, material);

        private static Transform Sphere(string name, Transform parent, Vector3 position, Vector3 scale, Material material)
            => Shape(PrimitiveType.Sphere, name, parent, position, scale, material);

        private static Transform Cylinder(string name, Transform parent, Vector3 position, float radius, float height,
            Material material, Quaternion? rotation = null)
            => Shape(PrimitiveType.Cylinder, name, parent, position, new Vector3(radius * 2, height * .5f, radius * 2), material, rotation);

        private Transform Ring(string name, Transform parent, Vector3 position, float radius, float tube,
            Material material, Quaternion rotation)
        {
            const int segments = 40, sides = 6;
            var vertices = new Vector3[(segments + 1) * (sides + 1)];
            var triangles = new int[segments * sides * 6];
            int index = 0;
            for (int i = 0; i <= segments; i++)
            {
                float a = i * Mathf.PI * 2 / segments;
                for (int j = 0; j <= sides; j++)
                {
                    float b = j * Mathf.PI * 2 / sides;
                    float r = radius + Mathf.Cos(b) * tube;
                    vertices[i * (sides + 1) + j] = new Vector3(Mathf.Cos(a) * r, Mathf.Sin(b) * tube, Mathf.Sin(a) * r);
                    if (i == segments || j == sides) continue;
                    int v = i * (sides + 1) + j;
                    triangles[index++] = v;
                    triangles[index++] = v + sides + 1;
                    triangles[index++] = v + 1;
                    triangles[index++] = v + 1;
                    triangles[index++] = v + sides + 1;
                    triangles[index++] = v + sides + 2;
                }
            }
            var mesh = new Mesh { name = name + " mesh", vertices = vertices, triangles = triangles };
            mesh.RecalculateNormals();
            var result = Group(name, parent, position);
            result.localRotation = rotation;
            result.gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            result.gameObject.AddComponent<MeshRenderer>().sharedMaterial = material;
            return result;
        }

        public Transform BuildCourtyard(Transform parent, int columns, int rows)
        {
            float width = columns * 2, depth = rows * 2;
            var world = Group("Sanctuary courtyard - procedural art draft", parent, Vector3.zero);
            Box("Courtyard foundation", world, new Vector3(width / 2, -.45f, depth / 2), new Vector3(width + 2, .8f, depth + 2), StoneDark);
            var paving = Group("Paving", world, Vector3.zero);
            var random = new System.Random(8041);
            for (int x = 0; x < columns; x++)
                for (int y = 0; y < rows; y++)
                    Box("Flagstone", paving, new Vector3(x * 2 + 1, -.025f, y * 2 + 1),
                        new Vector3(1.94f, .13f, 1.94f), random.NextDouble() > .12 ? Stone : StoneDark);
            CombineStatic(paving);

            var perimeter = Group("Perimeter architecture and flora", world, Vector3.zero);
            for (int x = 3; x < columns; x += 4)
            {
                Column(perimeter, new Vector3(x * 2, 0, -2.4f), 6.5f, .9f);
                Column(perimeter, new Vector3(x * 2, 0, depth + 2.4f), 6.5f, .9f);
                if (x + 4 < columns)
                {
                    Box("Entablature", perimeter, new Vector3(x * 2 + 4, 6.7f, -2.4f), new Vector3(8.3f, .65f, 2f), Stone);
                    Box("Entablature", perimeter, new Vector3(x * 2 + 4, 6.7f, depth + 2.4f), new Vector3(8.3f, .65f, 2f), Stone);
                }
            }
            for (int i = 0; i < 96; i++)
            {
                float x = (float)random.NextDouble() * width;
                float z = i % 2 == 0 ? -2.2f - (float)random.NextDouble() * 2 : depth + 2.2f + (float)random.NextDouble() * 2;
                FlowerCluster(perimeter, new Vector3(x, 0, z), random);
            }
            for (int i = 0; i < 12; i++)
            {
                float z = i * depth / 12;
                Cypress(perimeter, new Vector3(-4f, 0, z), 5 + (float)random.NextDouble() * 3);
                Cypress(perimeter, new Vector3(width + 6, 0, z), 5 + (float)random.NextDouble() * 3);
            }
            CombineStatic(perimeter);

            var skyline = Group("Distant alpine forms", world, Vector3.zero);
            for (int i = 0; i < 9; i++)
            {
                float height = 11 + (float)random.NextDouble() * 14;
                Sphere("Mountain", skyline, new Vector3(i * 15 - 20, height / 3 - 3, depth + 34),
                    new Vector3(20, height, 15), StoneDark);
            }
            CombineStatic(skyline);
            return world;
        }

        private void Column(Transform parent, Vector3 position, float height, float radius)
        {
            var column = Group("Fluted column", parent, position);
            Box("Plinth", column, Vector3.up * .22f, new Vector3(radius * 2.8f, .44f, radius * 2.8f), Stone);
            Cylinder("Base", column, Vector3.up * .55f, radius * 1.2f, .22f, Stone);
            Cylinder("Shaft", column, Vector3.up * (height * .5f), radius * .85f, height - 1, Stone);
            for (int i = 0; i < 12; i++)
            {
                float a = i * Mathf.PI / 6;
                Cylinder("Flute", column, new Vector3(Mathf.Cos(a) * radius * .76f, height * .5f, Mathf.Sin(a) * radius * .76f),
                    radius * .11f, height - 1.2f, Stone);
            }
            Cylinder("Capital collar", column, Vector3.up * (height - .45f), radius * 1.12f, .32f, Stone);
            for (int i = 0; i < 8; i++)
            {
                float a = i * Mathf.PI / 4;
                var leaf = Sphere("Capital leaf", column, new Vector3(Mathf.Cos(a) * radius, height - .55f, Mathf.Sin(a) * radius),
                    new Vector3(radius * .35f, radius * .65f, radius * .25f), Stone);
                leaf.localRotation = Quaternion.Euler(18, -a * Mathf.Rad2Deg, 0);
            }
            Box("Abacus", column, Vector3.up * height, new Vector3(radius * 2.6f, .25f, radius * 2.6f), Stone);
        }

        private void Cypress(Transform parent, Vector3 position, float height)
        {
            Cylinder("Cypress trunk", parent, position + Vector3.up, .22f, 2, Iron);
            Sphere("Cypress crown", parent, position + Vector3.up * height * .52f, new Vector3(1.8f, height, 1.8f), Leaf);
        }

        private void FlowerCluster(Transform parent, Vector3 position, System.Random random)
        {
            Sphere("Leaf mass", parent, position + Vector3.up * .28f, new Vector3(1.6f, .65f, 1.3f), Leaf);
            for (int f = 0; f < 3; f++)
            {
                var center = position + new Vector3((float)random.NextDouble() - .5f, .55f + (float)random.NextDouble() * .5f,
                    (float)random.NextDouble() - .5f);
                Material petals = random.NextDouble() > .42 ? Gold : Pink;
                for (int p = 0; p < 7; p++)
                {
                    float a = p * Mathf.PI * 2 / 7;
                    Sphere("Flower petal", parent, center + new Vector3(Mathf.Cos(a) * .2f, 0, Mathf.Sin(a) * .2f),
                        new Vector3(.32f, .16f, .32f), petals);
                }
                Sphere("Flower center", parent, center + Vector3.up * .06f, Vector3.one * .2f, Gold);
            }
        }

        public TowerView Tower(Transform parent, Vector3 position)
        {
            var root = Group("Petal Gatling - procedural stand-in", parent, position);
            Column(root, Vector3.zero, 1.55f, .54f);
            var turret = Group("Yaw mount", root, Vector3.up * 1.85f);
            Cylinder("Turntable", turret, Vector3.zero, .64f, .18f, Brass);
            Box("Cradle", turret, new Vector3(0, .25f, 0), new Vector3(.7f, .52f, .85f), Brass);
            var barrels = Group("Rotary barrel assembly", turret, new Vector3(0, .37f, .6f));
            for (int i = 0; i < 6; i++)
            {
                float a = i * Mathf.PI / 3;
                Cylinder("Steel barrel", barrels, new Vector3(Mathf.Cos(a) * .16f, Mathf.Sin(a) * .16f, .4f), .047f, 1.15f,
                    Iron, Quaternion.Euler(90, 0, 0));
            }
            Ring("Brass barrel band", barrels, new Vector3(0, 0, .85f), .22f, .045f, Brass, Quaternion.Euler(90, 0, 0));
            Ring("Gear housing", turret, new Vector3(.39f, .2f, -.05f), .28f, .06f, Brass, Quaternion.Euler(0, 0, 90));
            Sphere("Mana crystal", turret, new Vector3(0, .78f, -.15f), new Vector3(.26f, .58f, .26f), Teal);
            return new TowerView { Root = root, Turret = turret, Barrels = barrels,
                Muzzle = Group("Muzzle", barrels, new Vector3(0, 0, 1f)) };
        }

        public Transform Enemy(Transform parent, bool isAir)
        {
            var root = Group(isAir ? "Rotor drone - stand-in" : "Skitter scout - stand-in", parent, Vector3.zero);
            Sphere("Armored chassis", root, new Vector3(0, .7f, 0), new Vector3(.8f, .55f, .95f), Iron);
            Ring("Armor girdle", root, new Vector3(0, .7f, 0), .4f, .055f, Brass, Quaternion.identity);
            Sphere("Optic", root, new Vector3(0, .74f, .45f), new Vector3(.24f, .18f, .12f), Amber);
            if (isAir)
            {
                Box("Rotor strut", root, Vector3.up * .85f, new Vector3(1.65f, .1f, .14f), Brass);
                for (int side = -1; side <= 1; side += 2)
                    Box("Rotor", root, new Vector3(side * .75f, 1.05f, 0), new Vector3(.15f, .04f, 1.05f), Iron);
            }
            else
                for (int side = -1; side <= 1; side += 2)
                    for (int i = 0; i < 3; i++)
                    {
                        float z = (i - 1) * .34f;
                        var leg = Box("Articulated leg", root, new Vector3(side * .48f, .36f, z), new Vector3(.12f, .6f, .12f), Brass);
                        leg.localRotation = Quaternion.Euler(0, 0, side * 40);
                        Sphere("Foot", root, new Vector3(side * .7f, .08f, z), new Vector3(.2f, .12f, .24f), Iron);
                    }
            return root;
        }

        public Transform Sanctum(Transform parent, Vector3 position)
        {
            var root = Group("Verdant Sanctum - procedural stand-in", parent, position);
            Cylinder("Lower stair", root, Vector3.up * .1f, 3.4f, .2f, StoneDark);
            Cylinder("Upper stair", root, Vector3.up * .3f, 2.9f, .25f, Stone);
            for (int i = 0; i < 8; i++)
            {
                float a = i * Mathf.PI / 4;
                Column(root, new Vector3(Mathf.Cos(a) * 2.2f, .4f, Mathf.Sin(a) * 2.2f), 5.1f, .32f);
            }
            Ring("Stone crown", root, Vector3.up * 5.6f, 2.3f, .32f, Stone, Quaternion.identity);
            Ring("Armillary orbit A", root, Vector3.up * 2.9f, 1.2f, .08f, Brass, Quaternion.Euler(65, 20, 0));
            Ring("Armillary orbit B", root, Vector3.up * 2.9f, 1.45f, .065f, Brass, Quaternion.Euler(10, 20, 75));
            Sphere("Aether heart", root, Vector3.up * 2.9f, new Vector3(.75f, 1.7f, .75f), Teal);
            return root;
        }

        private static void CombineStatic(Transform parent)
        {
            var byMaterial = new Dictionary<Material, List<CombineInstance>>();
            var originalMeshes = new List<Mesh>();
            foreach (var filter in parent.GetComponentsInChildren<MeshFilter>())
            {
                var renderer = filter.GetComponent<MeshRenderer>();
                if (renderer == null || filter.sharedMesh == null) continue;
                if (!byMaterial.TryGetValue(renderer.sharedMaterial, out var list))
                {
                    list = new List<CombineInstance>();
                    byMaterial.Add(renderer.sharedMaterial, list);
                }
                list.Add(new CombineInstance { mesh = filter.sharedMesh,
                    transform = parent.worldToLocalMatrix * filter.transform.localToWorldMatrix });
                renderer.enabled = false;
                if (filter.sharedMesh.name.EndsWith(" mesh")) originalMeshes.Add(filter.sharedMesh);
            }
            foreach (var pair in byMaterial)
            {
                var mesh = new Mesh { name = "Combined " + pair.Key.name, indexFormat = IndexFormat.UInt32 };
                mesh.CombineMeshes(pair.Value.ToArray(), true, true);
                var result = Group(mesh.name, parent, Vector3.zero);
                result.gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
                result.gameObject.AddComponent<MeshRenderer>().sharedMaterial = pair.Key;
            }
            // Meshes created by this factory are released after combining; Unity owns primitive meshes.
            foreach (var mesh in originalMeshes) Object.Destroy(mesh);
            for (int i = parent.childCount - 1; i >= 0; i--)
            {
                var child = parent.GetChild(i);
                if (!child.name.StartsWith("Combined ")) Object.Destroy(child.gameObject);
            }
        }

        public void Dispose()
        {
            foreach (var material in ownedMaterials) if (material != null) Object.Destroy(material);
            ownedMaterials.Clear();
        }
    }
}
