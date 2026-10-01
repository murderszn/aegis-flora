using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.UI;

namespace AegisFlorae.Slice
{
    /// <summary>Playable native three-wave prototype. Generated geometry is explicitly temporary art.</summary>
    public sealed class SanctuarySlice : MonoBehaviour
    {
        private const float CellSize = 2f;
        private const float Step = 1f / 60;
        private SliceSimulation simulation;
        private SliceArtFactory art;
        private Transform actors;
        private Transform sanctum;
        private Camera viewCamera;
        private Vector3 cameraTarget;
        private Vector3 cameraOffset = new Vector3(-38, 60, -38);
        private bool paused, selling, placing = true;
        private int speed = 1;
        private float accumulator, animationTime;
        private string message = "Place Gatlings beside the entry route, then call the first wave.";
        private LineRenderer pathLine, hoverLine;
        private Material lineMaterial;
        private Material hoverMaterial;
        private Material tracerMaterial;
        private TMP_FontAsset font;
        private VolumeProfile volumeProfile;
        private TextMeshProUGUI counters, status, modeText, notice;
        private Button waveButton;
        private TextMeshProUGUI waveLabel, pauseLabel, speedLabel;
        private readonly Dictionary<int, SliceArtFactory.TowerView> towers = new Dictionary<int, SliceArtFactory.TowerView>();
        private readonly Dictionary<int, Transform> enemies = new Dictionary<int, Transform>();
        private readonly Queue<Transform> scoutPool = new Queue<Transform>();
        private readonly Queue<Transform> airPool = new Queue<Transform>();
        private readonly Dictionary<int, bool> airKinds = new Dictionary<int, bool>();
        private readonly Dictionary<int, LineRenderer> shots = new Dictionary<int, LineRenderer>();
        private readonly Dictionary<int, float> shotTimers = new Dictionary<int, float>();
        private readonly List<int> removals = new List<int>();
        private readonly HashSet<int> activeIds = new HashSet<int>();
        private readonly HashSet<int> firedThisFrame = new HashSet<int>();
        private GridCell? hoverCell;

        public SliceSimulation Simulation => simulation;
        public bool IsPaused => paused;
        public int SimulationSpeed => speed;

        private void Start()
        {
            art = new SliceArtFactory();
            simulation = new SliceSimulation();
            simulation.ShotFired += OnShot;
            art.BuildCourtyard(transform, simulation.Columns, simulation.Rows);
            actors = SliceArtFactory.Group("Simulation views", transform, Vector3.zero);
            Vector3 goal = CellWorld(simulation.Goal);
            // Ornament sits beyond the logical board; it never blocks a combat cell.
            sanctum = art.Sanctum(transform, new Vector3(simulation.Columns * CellSize + 4, 0, goal.z));
            SetupCameraAndLight();
            lineMaterial = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
            lineMaterial.SetColor("_BaseColor", new Color(.15f, .8f, .72f));
            hoverMaterial = new Material(lineMaterial);
            tracerMaterial = new Material(lineMaterial);
            tracerMaterial.SetColor("_BaseColor", new Color(1, .72f, .22f));
            pathLine = Line("Validated route", .07f);
            hoverLine = Line("Placement footprint", .1f);
            hoverLine.sharedMaterial = hoverMaterial;
            SetupHud();
            RefreshPath();
        }

        private void SetupCameraAndLight()
        {
            cameraTarget = new Vector3(simulation.Columns, 0, simulation.Rows);
            var cameraObject = new GameObject("Tactical camera");
            cameraObject.transform.SetParent(transform, false);
            cameraObject.tag = "MainCamera";
            viewCamera = cameraObject.AddComponent<Camera>();
            viewCamera.orthographic = true;
            viewCamera.orthographicSize = 34;
            viewCamera.nearClipPlane = .1f;
            viewCamera.farClipPlane = 250;
            viewCamera.clearFlags = CameraClearFlags.SolidColor;
            viewCamera.backgroundColor = new Color(.035f, .14f, .18f);
            viewCamera.allowHDR = true;
            cameraObject.AddComponent<AudioListener>();
            var cameraData = cameraObject.AddComponent<UniversalAdditionalCameraData>();
            cameraData.renderPostProcessing = true;
            UpdateCamera();

            var sun = new GameObject("Warm late afternoon sun");
            sun.transform.SetParent(transform, false);
            sun.transform.rotation = Quaternion.Euler(48, -32, 0);
            var light = sun.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = new Color(1, .88f, .67f);
            light.intensity = 1.7f;
            light.shadows = LightShadows.Soft;
            light.shadowStrength = .72f;
            RenderSettings.sun = light;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.19f, .3f, .34f);
            RenderSettings.ambientEquatorColor = new Color(.09f, .16f, .16f);
            RenderSettings.ambientGroundColor = new Color(.045f, .065f, .06f);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = viewCamera.backgroundColor;
            RenderSettings.fogStartDistance = 100;
            RenderSettings.fogEndDistance = 220;

            var volume = new GameObject("Courtyard grade");
            volume.transform.SetParent(transform, false);
            var globalVolume = volume.AddComponent<Volume>();
            globalVolume.isGlobal = true;
            volumeProfile = ScriptableObject.CreateInstance<VolumeProfile>();
            globalVolume.sharedProfile = volumeProfile;
            var tone = volumeProfile.Add<Tonemapping>();
            tone.mode.Override(TonemappingMode.ACES);
            var bloom = volumeProfile.Add<Bloom>();
            bloom.threshold.Override(1.15f);
            bloom.intensity.Override(.25f);
            var color = volumeProfile.Add<ColorAdjustments>();
            color.contrast.Override(10);
            color.saturation.Override(-5);
        }

        private void UpdateCamera()
        {
            if (viewCamera == null) return;
            viewCamera.transform.position = cameraTarget + cameraOffset;
            viewCamera.transform.LookAt(cameraTarget);
        }

        private LineRenderer Line(string name, float width)
        {
            var item = new GameObject(name);
            item.transform.SetParent(transform, false);
            var line = item.AddComponent<LineRenderer>();
            line.sharedMaterial = lineMaterial;
            line.startWidth = line.endWidth = width;
            line.useWorldSpace = true;
            line.numCornerVertices = 3;
            line.numCapVertices = 3;
            line.shadowCastingMode = ShadowCastingMode.Off;
            return line;
        }

        private void Update()
        {
            if (simulation == null) return;
            HandleInput();
            firedThisFrame.Clear();
            float visualDelta = paused ? 0 : Mathf.Min(Time.deltaTime, .1f) * speed;
            if (!paused)
            {
                accumulator += visualDelta;
                while (accumulator >= Step)
                {
                    simulation.Tick(Step);
                    accumulator -= Step;
                }
                animationTime += visualDelta;
            }
            SynchronizeViews(visualDelta);
            RefreshHud();
        }

        private void HandleInput()
        {
            var keyboard = Keyboard.current;
            var mouse = Mouse.current;
            if (keyboard != null)
            {
                if (keyboard.qKey.wasPressedThisFrame || keyboard.digit1Key.wasPressedThisFrame) SelectBuild();
                if (keyboard.xKey.wasPressedThisFrame) SelectSell();
                if (keyboard.spaceKey.wasPressedThisFrame) CallWave();
                if (keyboard.pKey.wasPressedThisFrame) paused = !paused;
                if (keyboard.vKey.wasPressedThisFrame) CycleSpeed();
                if (keyboard.escapeKey.wasPressedThisFrame) { placing = false; selling = false; }
                float x = (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed ? 1 : 0)
                    - (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed ? 1 : 0);
                float y = (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed ? 1 : 0)
                    - (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed ? 1 : 0);
                var right = viewCamera.transform.right;
                var forward = Vector3.ProjectOnPlane(viewCamera.transform.forward, Vector3.up).normalized;
                cameraTarget += (right * x + forward * y) * (Time.unscaledDeltaTime * 18);
                cameraTarget.x = Mathf.Clamp(cameraTarget.x, 0, simulation.Columns * CellSize);
                cameraTarget.z = Mathf.Clamp(cameraTarget.z, 0, simulation.Rows * CellSize);
                UpdateCamera();
            }
            if (mouse == null) return;
            Vector2 pointer = mouse.position.ReadValue();
            bool overUi = EventSystem.current != null && EventSystem.current.IsPointerOverGameObject();
            // Explicit screen bands protect UI clicks even before the UI module's first pointer update.
            float canvasScale = Mathf.Min(Screen.width / 1920f, Screen.height / 1080f);
            overUi |= pointer.y < 188 * canvasScale || pointer.y > Screen.height - 82 * canvasScale;
            if (!overUi)
            {
                float zoom = mouse.scroll.ReadValue().y;
                viewCamera.orthographicSize = Mathf.Clamp(viewCamera.orthographicSize - zoom * .025f, 12, 48);
            }
            var ground = new Plane(Vector3.up, Vector3.zero);
            Ray ray = viewCamera.ScreenPointToRay(pointer);
            hoverCell = null;
            if (!overUi && ground.Raycast(ray, out float distance))
            {
                var point = ray.GetPoint(distance);
                var cell = new GridCell(Mathf.FloorToInt(point.x / CellSize), Mathf.FloorToInt(point.z / CellSize));
                if (cell.X >= 0 && cell.Y >= 0 && cell.X < simulation.Columns && cell.Y < simulation.Rows)
                    hoverCell = cell;
            }
            if (mouse.rightButton.wasPressedThisFrame) { placing = false; selling = false; }
            if (mouse.leftButton.wasPressedThisFrame && hoverCell.HasValue && (placing || selling))
            {
                if (paused) message = "Resume before changing the maze.";
                else if (simulation.Phase == SlicePhase.Victory || simulation.Phase == SlicePhase.Defeat)
                    message = "The match has ended. Restart to build another maze.";
                else if (selling) SellAt(hoverCell.Value);
                else
                {
                    string failure = simulation.GetPlacementFailure(hoverCell.Value);
                    if (simulation.TryPlaceTower(hoverCell.Value))
                    {
                        message = "Gatling deployed. Extend the route to keep enemies under fire.";
                        RefreshPath();
                    }
                    else message = failure;
                }
            }
            DrawHover();
        }

        private void SelectBuild() { placing = true; selling = false; }
        private void SelectSell() { selling = true; placing = false; }
        private void CycleSpeed() { speed = speed == 1 ? 2 : speed == 2 ? 4 : 1; }

        private void CallWave()
        {
            if (paused) { message = "Resume before calling a wave."; return; }
            message = simulation.StartNextWave() ? "The automata approach. Build along their route."
                : "Finish the current wave first, or restart a completed match.";
        }

        private void SellAt(GridCell cell)
        {
            for (int i = 0; i < simulation.Towers.Count; i++)
                if (simulation.Towers[i].Cell.Equals(cell))
                {
                    if (simulation.TrySellTower(simulation.Towers[i].Id))
                    {
                        message = "Tower reclaimed. Five Scrap returned.";
                        RefreshPath();
                    }
                    return;
                }
            message = "Select an existing Gatling to reclaim it.";
        }

        private void Restart()
        {
            simulation.ShotFired -= OnShot;
            foreach (var tower in towers.Values) ReleaseView(tower.Root);
            foreach (var shot in shots.Values) Destroy(shot.gameObject);
            foreach (var enemy in enemies.Values) ReleaseView(enemy);
            towers.Clear(); shots.Clear(); shotTimers.Clear(); enemies.Clear(); airKinds.Clear();
            simulation = new SliceSimulation();
            simulation.ShotFired += OnShot;
            paused = false; speed = 1; placing = true; selling = false; accumulator = 0;
            message = "A new sanctuary awaits. Place Gatlings, then call a wave.";
            RefreshPath();
        }

        private void RefreshPath()
        {
            var path = simulation.GetPath(simulation.Spawn);
            pathLine.positionCount = path.Count;
            for (int i = 0; i < path.Count; i++) pathLine.SetPosition(i, CellWorld(path[i]) + Vector3.up * .14f);
        }

        private void DrawHover()
        {
            hoverLine.enabled = hoverCell.HasValue && (placing || selling);
            if (!hoverLine.enabled) return;
            var cell = hoverCell.Value;
            var color = selling ? new Color(1, .62f, .2f) : simulation.CanPlaceTower(cell) ? new Color(.15f, .95f, .7f) : new Color(1, .25f, .2f);
            hoverLine.startColor = hoverLine.endColor = color;
            hoverMaterial.SetColor("_BaseColor", color);
            var origin = new Vector3(cell.X * CellSize, .18f, cell.Y * CellSize);
            hoverLine.positionCount = 5;
            hoverLine.SetPosition(0, origin);
            hoverLine.SetPosition(1, origin + Vector3.right * CellSize);
            hoverLine.SetPosition(2, origin + new Vector3(CellSize, 0, CellSize));
            hoverLine.SetPosition(3, origin + Vector3.forward * CellSize);
            hoverLine.SetPosition(4, origin);
        }

        private static Vector3 CellWorld(GridCell cell) => new Vector3((cell.X + .5f) * CellSize, 0, (cell.Y + .5f) * CellSize);

        private void SynchronizeViews(float delta)
        {
            activeIds.Clear();
            for (int i = 0; i < simulation.Towers.Count; i++)
            {
                var tower = simulation.Towers[i];
                activeIds.Add(tower.Id);
                EnsureTowerView(tower);
                // Keep brief telemetry visible for one presentation frame even at 4x speed.
                float remaining = firedThisFrame.Contains(tower.Id) ? .075f
                    : Mathf.Max(0, shotTimers[tower.Id] - (paused ? 0 : Time.unscaledDeltaTime));
                shotTimers[tower.Id] = remaining;
                shots[tower.Id].enabled = remaining > 0;
                if (remaining > 0) towers[tower.Id].Barrels.Rotate(0, 0, delta * 900, Space.Self);
            }
            removals.Clear();
            foreach (int id in towers.Keys) if (!activeIds.Contains(id)) removals.Add(id);
            foreach (int id in removals)
            {
                ReleaseView(towers[id].Root); Destroy(shots[id].gameObject);
                towers.Remove(id); shots.Remove(id); shotTimers.Remove(id);
            }

            activeIds.Clear();
            for (int i = 0; i < simulation.Enemies.Count; i++)
            {
                var enemy = simulation.Enemies[i];
                if (!enemy.Alive) continue;
                activeIds.Add(enemy.Id);
                if (!enemies.TryGetValue(enemy.Id, out var root))
                {
                    var pool = enemy.IsAir ? airPool : scoutPool;
                    root = pool.Count > 0 ? pool.Dequeue() : art.Enemy(actors, enemy.IsAir);
                    root.gameObject.SetActive(true);
                    enemies.Add(enemy.Id, root);
                    airKinds.Add(enemy.Id, enemy.IsAir);
                }
                var position = new Vector3(enemy.X * CellSize, enemy.IsAir ? 3.2f : 0, enemy.Y * CellSize);
                var direction = position - root.position;
                direction.y = 0;
                if (direction.sqrMagnitude > .0001f) root.rotation = Quaternion.LookRotation(direction);
                root.position = position + Vector3.up * (Mathf.Sin(animationTime * 12 + enemy.Id) * .045f);
            }
            removals.Clear();
            foreach (int id in enemies.Keys) if (!activeIds.Contains(id)) removals.Add(id);
            foreach (int id in removals)
            {
                var enemy = enemies[id];
                enemy.gameObject.SetActive(false);
                (airKinds[id] ? airPool : scoutPool).Enqueue(enemy);
                enemies.Remove(id); airKinds.Remove(id);
            }
            // The Sanctum is scenery; its armillary rings are animated independently of the maze.
            if (sanctum != null && delta > 0)
                for (int i = 0; i < sanctum.childCount; i++)
                    if (sanctum.GetChild(i).name.StartsWith("Armillary orbit"))
                        sanctum.GetChild(i).Rotate(Vector3.up, delta * 12, Space.World);
        }

        private void OnShot(int towerId, int enemyId)
        {
            if (!towers.ContainsKey(towerId))
                for (int i = 0; i < simulation.Towers.Count; i++)
                    if (simulation.Towers[i].Id == towerId) { EnsureTowerView(simulation.Towers[i]); break; }
            if (!towers.TryGetValue(towerId, out var view) || !shots.TryGetValue(towerId, out var tracer)) return;
            // The current step may have just spawned (or be about to kill) the target.
            // Query authoritative coordinates inside the event, rather than last frame's render list.
            if (simulation.TryGetEnemyPosition(enemyId, out float x, out float y, out bool isAir))
            {
                var target = new Vector3(x * CellSize, isAir ? 3.9f : .8f, y * CellSize);
                var direction = target - view.Turret.position;
                direction.y = 0;
                if (direction.sqrMagnitude > .001f) view.Turret.rotation = Quaternion.LookRotation(direction);
                tracer.SetPosition(0, view.Muzzle.position);
                tracer.SetPosition(1, target);
                shotTimers[towerId] = .075f;
                firedThisFrame.Add(towerId);
            }
        }

        private void EnsureTowerView(TowerState tower)
        {
            if (towers.ContainsKey(tower.Id)) return;
            towers.Add(tower.Id, art.Tower(actors, CellWorld(tower.Cell)));
            var shot = Line("Gatling tracer", .045f);
            shot.sharedMaterial = tracerMaterial;
            shot.positionCount = 2;
            shot.startColor = shot.endColor = new Color(1, .8f, .3f);
            shot.enabled = false;
            shots.Add(tower.Id, shot);
            shotTimers.Add(tower.Id, 0);
        }

        private void SetupHud()
        {
            font = TMP_FontAsset.CreateFontAsset(Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"));
            var canvasObject = new GameObject("Aegis HUD", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            canvasObject.transform.SetParent(transform, false);
            var canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.Expand;
            if (FindFirstObjectByType<EventSystem>() == null)
            {
                var events = new GameObject("UI input", typeof(EventSystem), typeof(InputSystemUIInputModule));
                events.transform.SetParent(transform, false);
                events.GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
            }
            var top = Panel(canvasObject.transform, "Header", new Vector2(.5f, 1), new Vector2(0, -41), new Vector2(0, 82));
            StretchHorizontal(top);
            Label(top, "AEGIS FLORAE", new Vector2(28, 4), new Vector2(430, 48), 28, TextAlignmentOptions.MidlineLeft, new Vector2(0, .5f));
            counters = Label(top, "", new Vector2(-28, 8), new Vector2(760, 40), 22, TextAlignmentOptions.MidlineRight, new Vector2(1, .5f));
            var dock = Panel(canvasObject.transform, "Command dock", new Vector2(.5f, 0), new Vector2(0, 94), new Vector2(0, 188));
            StretchHorizontal(dock);
            status = Label(dock, "", new Vector2(26, 62), new Vector2(1000, 34), 21, TextAlignmentOptions.MidlineLeft, new Vector2(0, .5f));
            modeText = Label(dock, "", new Vector2(-26, 62), new Vector2(650, 34), 17, TextAlignmentOptions.MidlineRight, new Vector2(1, .5f));
            Button(dock, "PETAL GATLING · 6 SCRAP", new Vector2(-690, 9), new Vector2(330, 50), SelectBuild, out _);
            Button(dock, "RECLAIM · X", new Vector2(-413, 9), new Vector2(205, 50), SelectSell, out _);
            waveButton = Button(dock, "CALL WAVE · SPACE", new Vector2(-125, 9), new Vector2(340, 50), CallWave, out waveLabel);
            Button(dock, "PAUSE · P", new Vector2(156, 9), new Vector2(190, 50), () => paused = !paused, out pauseLabel);
            Button(dock, "1× SPEED · V", new Vector2(370, 9), new Vector2(215, 50), CycleSpeed, out speedLabel);
            Button(dock, "RESTART", new Vector2(600, 9), new Vector2(205, 50), Restart, out _);
            notice = Label(dock, message, new Vector2(0, -42), new Vector2(1710, 28), 19, TextAlignmentOptions.Center);
            Label(dock, "WASD / ARROWS pan   ·   WHEEL zoom   ·   Q build   ·   RIGHT CLICK cancel   ·   3-WAVE SLICE / PROCEDURAL ART DRAFT",
                new Vector2(0, -74), new Vector2(1780, 22), 15, TextAlignmentOptions.Center);
        }

        private RectTransform Panel(Transform parent, string name, Vector2 anchor, Vector2 position, Vector2 size)
        {
            var item = new GameObject(name, typeof(RectTransform), typeof(Image));
            var rect = item.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = rect.anchorMax = anchor;
            rect.anchoredPosition = position;
            rect.sizeDelta = size;
            item.GetComponent<Image>().color = new Color(.025f, .085f, .095f, .97f);
            return rect;
        }

        private static void StretchHorizontal(RectTransform rect)
        {
            rect.anchorMin = new Vector2(0, rect.anchorMin.y);
            rect.anchorMax = new Vector2(1, rect.anchorMax.y);
        }

        private TextMeshProUGUI Label(Transform parent, string text, Vector2 position, Vector2 size, float fontSize,
            TextAlignmentOptions alignment, Vector2? anchor = null)
        {
            var item = new GameObject("Label", typeof(RectTransform), typeof(TextMeshProUGUI));
            var rect = item.GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = rect.anchorMax = anchor ?? new Vector2(.5f, .5f);
            rect.pivot = new Vector2((anchor ?? new Vector2(.5f, .5f)).x, .5f);
            rect.anchoredPosition = position;
            rect.sizeDelta = size;
            var label = item.GetComponent<TextMeshProUGUI>();
            label.font = font;
            label.text = text;
            label.fontSize = fontSize;
            label.alignment = alignment;
            label.color = new Color(.86f, .83f, .66f);
            label.raycastTarget = false;
            return label;
        }

        private Button Button(Transform parent, string text, Vector2 position, Vector2 size, UnityEngine.Events.UnityAction action,
            out TextMeshProUGUI label)
        {
            var rect = Panel(parent, text, new Vector2(.5f, .5f), position, size);
            rect.GetComponent<Image>().color = new Color(.08f, .18f, .18f);
            var button = rect.gameObject.AddComponent<Button>();
            button.targetGraphic = rect.GetComponent<Image>();
            button.onClick.AddListener(action);
            label = Label(rect, text, Vector2.zero, size - new Vector2(12, 0), 18, TextAlignmentOptions.Center);
            return button;
        }

        private void RefreshHud()
        {
            counters.text = $"SCRAP  {simulation.Scrap}     SANCTUM  {simulation.Lives} / 15     WAVE  {simulation.Wave} / 3";
            status.text = simulation.Phase == SlicePhase.Victory ? "SANCTUARY SECURED — slice complete"
                : simulation.Phase == SlicePhase.Defeat ? "THE SANCTUM HAS FALLEN — restart to try another maze"
                : paused ? "BATTLE PAUSED" : simulation.Phase == SlicePhase.Combat ? "DEFEND THE SANCTUARY" : "SHAPE YOUR LABYRINTH";
            modeText.text = selling ? "RECLAIM MODE · 75% REFUND" : placing ? "BUILD MODE · PETAL GATLING" : "CAMERA MODE · Q TO BUILD";
            notice.text = message;
            waveButton.interactable = !paused && simulation.Phase == SlicePhase.Preparing;
            waveLabel.text = simulation.Phase == SlicePhase.Combat ? "WAVE IN PROGRESS" : "CALL WAVE · SPACE";
            pauseLabel.text = paused ? "RESUME · P" : "PAUSE · P";
            speedLabel.text = $"{speed}× SPEED · V";
        }

        private void OnDestroy()
        {
            if (simulation != null) simulation.ShotFired -= OnShot;
            art?.Dispose();
            if (lineMaterial != null) Destroy(lineMaterial);
            if (hoverMaterial != null) Destroy(hoverMaterial);
            if (tracerMaterial != null) Destroy(tracerMaterial);
            if (font != null)
            {
                if (font.material != null) Destroy(font.material);
                foreach (var atlas in font.atlasTextures) if (atlas != null) Destroy(atlas);
                Destroy(font);
            }
            if (volumeProfile != null)
            {
                foreach (var component in volumeProfile.components) Destroy(component);
                Destroy(volumeProfile);
            }
            // Only meshes authored by the factory belong to this scene; built-in primitive meshes do not.
            foreach (var filter in GetComponentsInChildren<MeshFilter>(true))
                if (filter.sharedMesh != null && (filter.sharedMesh.name.StartsWith("Combined ") || filter.sharedMesh.name.EndsWith(" mesh")))
                    Destroy(filter.sharedMesh);
        }

        private static void ReleaseView(Transform view)
        {
            foreach (var filter in view.GetComponentsInChildren<MeshFilter>(true))
                if (filter.sharedMesh != null && filter.sharedMesh.name.EndsWith(" mesh")) Destroy(filter.sharedMesh);
            Destroy(view.gameObject);
        }
    }
}
