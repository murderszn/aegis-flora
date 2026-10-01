using System;
using System.Collections.Generic;

namespace AegisFlorae.Slice
{
    public struct GridCell : IEquatable<GridCell>
    {
        public readonly int X;
        public readonly int Y;

        public GridCell(int x, int y) { X = x; Y = y; }
        public bool Equals(GridCell other) { return X == other.X && Y == other.Y; }
        public override bool Equals(object obj) { return obj is GridCell && Equals((GridCell)obj); }
        public override int GetHashCode() { unchecked { return (X * 397) ^ Y; } }
        public override string ToString() { return "(" + X + ", " + Y + ")"; }
        public static bool operator ==(GridCell left, GridCell right) { return left.Equals(right); }
        public static bool operator !=(GridCell left, GridCell right) { return !left.Equals(right); }
    }

    public enum SlicePhase { Preparing, Combat, Victory, Defeat }
    public enum EnemyKind { Scout, Drone }

    // Reused render-facing values; they update in place at the end of Tick. Do not retain across ticks.
    // Positions use cell units, with each cell centered at x+.5,y+.5.
    public sealed class EnemyState
    {
        public int Id { get; private set; }
        public EnemyKind Kind { get; private set; }
        public float X { get; private set; }
        public float Y { get; private set; }
        public float HP { get; private set; }
        public float Health { get { return HP; } }
        public float MaxHP { get; private set; }
        public float MaxHealth { get { return MaxHP; } }
        public bool IsAir { get; private set; }
        public bool Alive { get; private set; }
        public GridCell CurrentCell { get; private set; }
        public GridCell TargetWaypoint { get; private set; }

        internal EnemyState(int id, EnemyKind kind, float x, float y, float health, float maxHealth,
            bool isAir, bool alive, GridCell currentCell, GridCell targetWaypoint)
        {
            Id = id; Kind = kind; X = x; Y = y; HP = health; MaxHP = maxHealth;
            IsAir = isAir; Alive = alive; CurrentCell = currentCell; TargetWaypoint = targetWaypoint;
        }

        internal void UpdateFrom(int id, EnemyKind kind, float x, float y, float health, float maxHealth,
            bool isAir, bool alive, GridCell currentCell, GridCell targetWaypoint)
        {
            Id = id; Kind = kind; X = x; Y = y; HP = health; MaxHP = maxHealth;
            IsAir = isAir; Alive = alive; CurrentCell = currentCell; TargetWaypoint = targetWaypoint;
        }
    }

    public sealed class TowerState
    {
        public int Id { get; private set; }
        public GridCell Cell { get; private set; }
        public float Health { get; private set; }
        public float MaxHealth { get; private set; }
        internal TowerState(int id, GridCell cell, float health, float maxHealth)
        { Id = id; Cell = cell; Health = health; MaxHealth = maxHealth; }
        internal void UpdateFrom(int id, GridCell cell, float health, float maxHealth)
        { Id = id; Cell = cell; Health = health; MaxHealth = maxHealth; }
    }

    /// <summary>
    /// Deterministic, engine-independent gameplay slice. One buildable Petal Gatling and
    /// Scout/Drones across three intentionally short demo waves; this is not 50-wave parity.
    /// </summary>
    public sealed class SliceSimulation
    {
        public const int TowerCost = 6;
        public const float SellRate = 0.75f;
        public const int DemoWaveLimit = 3;
        private const float GatlingRange = 2.8f;
        private const float GatlingDamage = 6f;
        private const float GatlingInterval = 0.12f;
        private const float ScoutHealth = 28f;
        private const float ScoutSpeedWorld = 2.7f;
        private const float ScoutBounty = 2f;
        private const int ScoutLeak = 1;
        private const float DroneHealth = 45f;
        private const float DroneSpeedWorld = 2.2f;
        private const float DroneBounty = 5f;
        private const int DroneLeak = 1;
        private static readonly int[] Dx = { 1, -1, 0, 0 };
        private static readonly int[] Dy = { 0, 0, 1, -1 };

        private sealed class Enemy
        {
            public int Id;
            public EnemyKind Kind;
            public float X, Y, Health, MaxHealth, SpeedWorld, Bounty, Radius;
            public int Leak;
            public bool IsAir, Alive = true;
            public GridCell CurrentCell, TargetWaypoint;
            public List<GridCell> Path;
            public int PathIndex;
        }

        private sealed class Tower
        {
            public int Id;
            public GridCell Cell;
            public float Cooldown;
        }

        private sealed class SpawnOrder
        {
            public float At;
            public EnemyKind Kind;
            public SpawnOrder(float at, EnemyKind kind) { At = at; Kind = kind; }
        }

        private readonly int columns, rows, waveLimit;
        private readonly int initialScrap, initialLives;
        private readonly bool[] blocked;
        private readonly int[] flowDistance, flowQueue, candidateDistance, candidateQueue;
        private readonly GridCell[] flowNext, candidateNext;
        private bool flowFieldDirty = true;
        private int flowFieldRebuildCount;
        private readonly List<Enemy> enemies = new List<Enemy>();
        private readonly List<Tower> towers = new List<Tower>();
        private readonly List<SpawnOrder> spawnQueue = new List<SpawnOrder>();
        private readonly List<EnemyState> enemyView = new List<EnemyState>();
        private readonly List<TowerState> towerView = new List<TowerState>();
        private readonly Stack<EnemyState> enemyViewPool = new Stack<EnemyState>();
        private readonly Stack<TowerState> towerViewPool = new Stack<TowerState>();
        private readonly IReadOnlyList<EnemyState> readOnlyEnemies;
        private readonly IReadOnlyList<TowerState> readOnlyTowers;
        private int nextEnemyId = 1, nextTowerId = 1;
        private float waveClock;

        public event Action<int, int> ShotFired;

        public int Columns { get { return columns; } }
        public int Rows { get { return rows; } }
        public GridCell Spawn { get; private set; }
        public GridCell Goal { get; private set; }
        public int Scrap { get; private set; }
        public int Lives { get; private set; }
        public int Wave { get; private set; }
        public SlicePhase Phase { get; private set; }
        public IReadOnlyList<EnemyState> Enemies { get { return readOnlyEnemies; } }
        public IReadOnlyList<TowerState> Towers { get { return readOnlyTowers; } }
        public int DemoWaveLimitValue { get { return waveLimit; } }
        internal int FlowFieldRebuildCount { get { return flowFieldRebuildCount; } }

        public bool CanPlaceTower(GridCell cell) { return GetPlacementFailure(cell) == null; }

        /// <summary>Reads live actor coordinates during synchronous simulation events such as ShotFired.</summary>
        public bool TryGetEnemyPosition(int enemyId, out float x, out float y, out bool isAir)
        {
            for (int i = 0; i < enemies.Count; i++)
            {
                Enemy enemy = enemies[i];
                if (enemy.Id != enemyId || !enemy.Alive) continue;
                x = enemy.X; y = enemy.Y; isAir = enemy.IsAir;
                return true;
            }
            x = 0f; y = 0f; isAir = false;
            return false;
        }

        /// <summary>Returns null when a tower can be built, otherwise a concise UI reason.</summary>
        public string GetPlacementFailure(GridCell cell)
        {
            if (Phase == SlicePhase.Victory || Phase == SlicePhase.Defeat) return "The match has ended.";
            if (!InBounds(cell)) return "Outside the battlefield.";
            if (cell == Spawn || cell == Goal) return "The spawn and Sanctum must stay clear.";
            if (blocked[Index(cell)]) return "A tower already occupies this tile.";
            if (Scrap < TowerCost) return "Not enough Scrap.";
            for (int i = 0; i < enemies.Count; i++)
            {
                Enemy e = enemies[i];
                if (!e.Alive || e.IsAir) continue;
                if (cell == e.CurrentCell) return "A ground enemy occupies this tile.";
                if (cell == e.TargetWaypoint) return "A ground enemy is moving into this tile.";
            }
            blocked[Index(cell)] = true;
            ComputeFlowField(blocked, candidateDistance, candidateNext, candidateQueue);
            bool valid = candidateDistance[Index(Spawn)] >= 0;
            if (valid)
            {
                for (int i = 0; i < enemies.Count; i++)
                {
                    Enemy e = enemies[i];
                    if (!e.Alive || e.IsAir) continue;
                    if (candidateDistance[Index(e.CurrentCell)] < 0 || candidateDistance[Index(e.TargetWaypoint)] < 0)
                    { valid = false; break; }
                }
            }
            blocked[Index(cell)] = false;
            return valid ? null : "This blocks every route for a ground unit.";
        }

        public SliceSimulation(int columns = 36, int rows = 20, GridCell? spawn = null,
            GridCell? goal = null, int startingScrap = 20, int startingLives = 15,
            int demoWaveLimit = DemoWaveLimit)
        {
            if (columns < 2 || rows < 1) throw new ArgumentOutOfRangeException("Grid must be at least 2 by 1.");
            if (startingScrap < 0 || startingLives < 1) throw new ArgumentOutOfRangeException("Starting resources are invalid.");
            if (demoWaveLimit < 1) throw new ArgumentOutOfRangeException("demoWaveLimit");
            this.columns = columns; this.rows = rows; waveLimit = demoWaveLimit;
            initialScrap = startingScrap; initialLives = startingLives;
            Spawn = spawn.HasValue ? spawn.Value : new GridCell(0, rows / 2);
            Goal = goal.HasValue ? goal.Value : new GridCell(columns - 1, rows / 2);
            if (!InBounds(Spawn) || !InBounds(Goal) || Spawn == Goal) throw new ArgumentException("Spawn and goal must be distinct cells inside the grid.");
            blocked = new bool[columns * rows];
            flowDistance = new int[blocked.Length]; flowNext = new GridCell[blocked.Length]; flowQueue = new int[blocked.Length];
            candidateDistance = new int[blocked.Length]; candidateNext = new GridCell[blocked.Length]; candidateQueue = new int[blocked.Length];
            Scrap = startingScrap; Lives = startingLives; Phase = SlicePhase.Preparing;
            readOnlyEnemies = enemyView.AsReadOnly(); readOnlyTowers = towerView.AsReadOnly();
            RefreshViews();
        }

        /// <summary>Preview a shortest cardinal route. Air units fly directly and ignore walls.</summary>
        public IReadOnlyList<GridCell> GetPath(GridCell start, bool air = false)
        {
            if (!InBounds(start)) return new GridCell[0];
            if (air) return new[] { start, Goal };
            EnsureFlowField();
            if (flowDistance[Index(start)] < 0) return new GridCell[0];
            var path = new List<GridCell>();
            var cell = start;
            for (int guard = 0; guard <= columns * rows; guard++)
            {
                path.Add(cell);
                if (cell == Goal) return path.AsReadOnly();
                var successor = flowNext[Index(cell)];
                if (!InBounds(successor) || successor == cell) return new GridCell[0];
                cell = successor;
            }
            return new GridCell[0];
        }

        /// <summary>Validates the new maze against spawn, goal, and every active ground unit before charging.</summary>
        public bool TryPlaceTower(GridCell cell)
        {
            if (Phase == SlicePhase.Victory || Phase == SlicePhase.Defeat || !InBounds(cell) ||
                cell == Spawn || cell == Goal || blocked[Index(cell)] || Scrap < TowerCost)
                return false;
            if (!CanPlaceTower(cell)) return false;
            blocked[Index(cell)] = true;
            flowFieldDirty = true;
            EnsureFlowField();

            Scrap -= TowerCost;
            towers.Add(new Tower { Id = nextTowerId++, Cell = cell });
            for (int i = 0; i < enemies.Count; i++)
            {
                Enemy e = enemies[i];
                if (!e.Alive || e.IsAir) continue;
                e.Path = BuildPath(e.TargetWaypoint, blocked);
                e.PathIndex = 0;
            }
            RefreshViews();
            return true;
        }

        public bool TrySellTower(int id)
        {
            int index = towers.FindIndex(t => t.Id == id);
            if (index < 0 || Phase == SlicePhase.Victory || Phase == SlicePhase.Defeat) return false;
            Tower tower = towers[index];
            towers.RemoveAt(index);
            blocked[Index(tower.Cell)] = false;
            flowFieldDirty = true;
            EnsureFlowField();
            Scrap += (int)Math.Round(TowerCost * SellRate, MidpointRounding.AwayFromZero);
            for (int i = 0; i < enemies.Count; i++)
            {
                Enemy e = enemies[i];
                if (e.Alive && !e.IsAir)
                {
                    e.Path = BuildPath(e.TargetWaypoint, blocked);
                    e.PathIndex = 0;
                }
            }
            RefreshViews();
            return true;
        }

        public bool StartNextWave()
        {
            if (Phase != SlicePhase.Preparing || Wave >= waveLimit) return false;
            Wave++;
            Phase = SlicePhase.Combat;
            waveClock = 0f;
            spawnQueue.Clear();
            int scouts = 5 + (int)Math.Floor(Wave * 1.6f) + (Wave <= 5 ? 2 : 0);
            for (int i = 0; i < scouts; i++) spawnQueue.Add(new SpawnOrder(i * 0.45f, EnemyKind.Scout));
            if (Wave >= 2)
            {
                int drones = Wave == 2 ? 1 : 2;
                float first = scouts * 0.45f;
                for (int i = 0; i < drones; i++) spawnQueue.Add(new SpawnOrder(first + i * 0.75f, EnemyKind.Drone));
            }
            spawnQueue.Sort(delegate(SpawnOrder a, SpawnOrder b) { return a.At.CompareTo(b.At); });
            return true;
        }

        public void Restart()
        {
            enemies.Clear(); towers.Clear(); spawnQueue.Clear();
            for (int i = enemyView.Count - 1; i >= 0; i--) enemyViewPool.Push(enemyView[i]);
            for (int i = towerView.Count - 1; i >= 0; i--) towerViewPool.Push(towerView[i]);
            enemyView.Clear(); towerView.Clear();
            Array.Clear(blocked, 0, blocked.Length);
            flowFieldDirty = true;
            nextEnemyId = 1; nextTowerId = 1; waveClock = 0f;
            Scrap = initialScrap; Lives = initialLives; Wave = 0; Phase = SlicePhase.Preparing;
        }

        /// <summary>Advances one fixed simulation step. The owner controls pause and speed by passing 0/scaled time.</summary>
        public void Tick(float dtSeconds)
        {
            if (dtSeconds < 0f || float.IsNaN(dtSeconds) || float.IsInfinity(dtSeconds)) throw new ArgumentOutOfRangeException("dtSeconds");
            if (dtSeconds == 0f || Phase == SlicePhase.Victory || Phase == SlicePhase.Defeat) return;
            float remaining = dtSeconds;
            // Substeps keep waypoint and weapon timing stable when caller supplies a larger fixed step.
            while (remaining > 0f && Phase != SlicePhase.Victory && Phase != SlicePhase.Defeat)
            {
                float step = Math.Min(remaining, 0.05f);
                SimulateStep(step);
                remaining -= step;
            }
            RefreshViews();
        }

        private void SpawnEnemy(EnemyKind kind)
        {
            bool air = kind == EnemyKind.Drone;
            float hp = air ? DroneHealth : ScoutHealth;
            List<GridCell> path = air ? null : BuildPath(Spawn, blocked);
            var enemy = new Enemy
            {
                Id = nextEnemyId++, Kind = kind, IsAir = air, Health = hp, MaxHealth = hp,
                SpeedWorld = air ? DroneSpeedWorld : ScoutSpeedWorld,
                Bounty = air ? DroneBounty : ScoutBounty, Leak = air ? DroneLeak : ScoutLeak,
                Radius = air ? 0.25f : 0.22f,
                X = Spawn.X + 0.5f, Y = Spawn.Y + 0.5f, CurrentCell = Spawn,
                TargetWaypoint = air ? Goal : (path.Count > 1 ? path[1] : Spawn), Path = path, PathIndex = 1
            };
            enemies.Add(enemy);
        }

        private void SimulateStep(float dt)
        {
            if (Phase == SlicePhase.Combat)
            {
                waveClock += dt;
                while (spawnQueue.Count > 0 && spawnQueue[0].At <= waveClock)
                {
                    SpawnEnemy(spawnQueue[0].Kind);
                    spawnQueue.RemoveAt(0);
                }
            }
            for (int i = 0; i < towers.Count; i++)
            {
                Tower tower = towers[i];
                tower.Cooldown = Math.Max(0f, tower.Cooldown - dt);
                if (tower.Cooldown > 0f) continue;
                Enemy target = FindTarget(tower);
                if (target == null) continue;
                float damage = GatlingDamage;
                if (target.Kind == EnemyKind.Scout) damage *= 1.25f; // Source Gatling kinetic modifier.
                damage *= ArmorMultiplier(target.Kind == EnemyKind.Drone ? 1 : 0);
                if (ShotFired != null) ShotFired(tower.Id, target.Id);
                target.Health -= damage;
                tower.Cooldown = GatlingInterval;
                if (target.Health <= 0f) Kill(target);
            }

            for (int i = 0; i < enemies.Count; i++)
            {
                Enemy e = enemies[i];
                if (Phase == SlicePhase.Defeat) break;
                if (!e.Alive) continue;
                if (e.IsAir)
                {
                    float targetX = Goal.X + 0.5f, targetY = Goal.Y + 0.5f;
                    float dx = targetX - e.X, dy = targetY - e.Y;
                    float distance = (float)Math.Sqrt(dx * dx + dy * dy);
                    float advance = e.SpeedWorld * dt;
                    if (distance <= advance) { e.X = targetX; e.Y = targetY; LeakEnemy(e); }
                    else { e.X += dx / distance * advance; e.Y += dy / distance * advance; e.CurrentCell = CellAt(e.X, e.Y); }
                    continue;
                }
                if (e.Path == null || e.Path.Count == 0) continue;
                if (e.PathIndex >= e.Path.Count) { LeakEnemy(e); continue; }
                GridCell targetCell = e.Path[e.PathIndex];
                e.TargetWaypoint = targetCell;
                float tx = targetCell.X + 0.5f, ty = targetCell.Y + 0.5f;
                float vx = tx - e.X, vy = ty - e.Y;
                float dist = (float)Math.Sqrt(vx * vx + vy * vy);
                float move = e.SpeedWorld * dt;
                if (dist <= move + 0.00001f)
                {
                    e.X = tx; e.Y = ty; e.CurrentCell = targetCell; e.PathIndex++;
                    if (targetCell == Goal) LeakEnemy(e);
                    else if (e.PathIndex < e.Path.Count) e.TargetWaypoint = e.Path[e.PathIndex];
                }
                else if (dist > 0f)
                {
                    e.X += vx / dist * move; e.Y += vy / dist * move;
                }
            }
            RemoveInactiveEnemies();
            if (Lives <= 0) Phase = SlicePhase.Defeat;
            if (Phase == SlicePhase.Combat && spawnQueue.Count == 0 && NoLivingEnemies())
                Phase = Wave >= waveLimit ? SlicePhase.Victory : SlicePhase.Preparing;
        }

        private Enemy FindTarget(Tower tower)
        {
            Enemy best = null;
            float bestRemaining = float.PositiveInfinity;
            float range = GatlingRange;
            float tx = tower.Cell.X + 0.5f, ty = tower.Cell.Y + 0.5f;
            for (int i = 0; i < enemies.Count; i++)
            {
                Enemy e = enemies[i];
                if (!e.Alive) continue;
                float dx = e.X - tx, dy = e.Y - ty;
                float targetRange = range + e.Radius;
                if ((dx * dx) + (dy * dy) > targetRange * targetRange) continue;
                float remaining;
                if (e.IsAir)
                {
                    float gx = Goal.X + 0.5f - e.X, gy = Goal.Y + 0.5f - e.Y;
                    remaining = (float)Math.Sqrt(gx * gx + gy * gy);
                }
                else
                {
                    EnsureFlowField();
                    GridCell waypoint = e.TargetWaypoint;
                    float wx = waypoint.X + 0.5f - e.X, wy = waypoint.Y + 0.5f - e.Y;
                    remaining = flowDistance[Index(waypoint)] + (float)Math.Sqrt(wx * wx + wy * wy);
                }
                if (best == null || remaining < bestRemaining || (remaining == bestRemaining && e.Id < best.Id))
                { best = e; bestRemaining = remaining; }
            }
            return best;
        }

        private void Kill(Enemy enemy)
        {
            if (!enemy.Alive) return;
            enemy.Alive = false;
            Scrap += (int)enemy.Bounty;
        }

        private void LeakEnemy(Enemy enemy)
        {
            if (!enemy.Alive) return;
            enemy.Alive = false;
            Lives = Math.Max(0, Lives - enemy.Leak);
            if (Lives == 0) Phase = SlicePhase.Defeat;
        }

        private bool NoLivingEnemies()
        {
            for (int i = 0; i < enemies.Count; i++) if (enemies[i].Alive) return false;
            return true;
        }

        private void RefreshViews()
        {
            for (int i = 0; i < enemies.Count; i++)
            {
                Enemy e = enemies[i];
                if (i >= enemyView.Count)
                {
                    EnemyState state = enemyViewPool.Count > 0 ? enemyViewPool.Pop()
                        : new EnemyState(e.Id, e.Kind, e.X, e.Y, 0f, e.MaxHealth, e.IsAir, e.Alive, e.CurrentCell, e.TargetWaypoint);
                    enemyView.Add(state);
                }
                enemyView[i].UpdateFrom(e.Id, e.Kind, e.X, e.Y, Math.Max(0f, e.Health), e.MaxHealth,
                    e.IsAir, e.Alive, e.CurrentCell, e.TargetWaypoint);
            }
            while (enemyView.Count > enemies.Count)
            {
                int last = enemyView.Count - 1;
                enemyViewPool.Push(enemyView[last]);
                enemyView.RemoveAt(last);
            }
            for (int i = 0; i < towers.Count; i++)
            {
                if (i >= towerView.Count)
                {
                    TowerState state = towerViewPool.Count > 0 ? towerViewPool.Pop()
                        : new TowerState(towers[i].Id, towers[i].Cell, 100f, 100f);
                    towerView.Add(state);
                }
                towerView[i].UpdateFrom(towers[i].Id, towers[i].Cell, 100f, 100f);
            }
            while (towerView.Count > towers.Count)
            {
                int last = towerView.Count - 1;
                towerViewPool.Push(towerView[last]);
                towerView.RemoveAt(last);
            }
        }

        private void RemoveInactiveEnemies()
        {
            for (int i = enemies.Count - 1; i >= 0; i--)
                if (!enemies[i].Alive) enemies.RemoveAt(i);
        }

        private bool InBounds(GridCell cell) { return cell.X >= 0 && cell.X < columns && cell.Y >= 0 && cell.Y < rows; }
        private int Index(GridCell cell) { return cell.Y * columns + cell.X; }
        private GridCell CellAt(float x, float y)
        {
            int cx = Math.Max(0, Math.Min(columns - 1, (int)Math.Floor(x)));
            int cy = Math.Max(0, Math.Min(rows - 1, (int)Math.Floor(y)));
            return new GridCell(cx, cy);
        }

        private void EnsureFlowField()
        {
            if (!flowFieldDirty) return;
            ComputeFlowField(blocked, flowDistance, flowNext, flowQueue);
            flowFieldDirty = false;
            flowFieldRebuildCount++;
        }

        private void ComputeFlowField(bool[] walls, int[] distance, GridCell[] next, int[] queue)
        {
            int count = columns * rows;
            for (int i = 0; i < count; i++) { distance[i] = -1; next[i] = new GridCell(-1, -1); }
            if (walls[Index(Goal)]) return;
            int head = 0, tail = 0;
            int goalIndex = Index(Goal); distance[goalIndex] = 0; next[goalIndex] = Goal; queue[tail++] = goalIndex;
            while (head < tail)
            {
                int currentIndex = queue[head++];
                int cx = currentIndex % columns, cy = currentIndex / columns;
                for (int d = 0; d < 4; d++)
                {
                    int nx = cx + Dx[d], ny = cy + Dy[d];
                    if (nx < 0 || nx >= columns || ny < 0 || ny >= rows) continue;
                    int ni = ny * columns + nx;
                    if (walls[ni] || distance[ni] >= 0) continue;
                    distance[ni] = distance[currentIndex] + 1;
                    next[ni] = new GridCell(cx, cy);
                    queue[tail++] = ni;
                }
            }
        }

        private List<GridCell> BuildPath(GridCell start, bool[] walls)
        {
            if (!InBounds(start)) return null;
            if (ReferenceEquals(walls, blocked)) EnsureFlowField();
            int[] distance = ReferenceEquals(walls, blocked) ? flowDistance : candidateDistance;
            GridCell[] next = ReferenceEquals(walls, blocked) ? flowNext : candidateNext;
            if (distance[Index(start)] < 0) return null;
            var path = new List<GridCell>(); GridCell cell = start;
            for (int guard = 0; guard <= columns * rows; guard++)
            {
                path.Add(cell);
                if (cell == Goal) return path;
                GridCell successor = next[Index(cell)];
                if (!InBounds(successor) || successor == cell) return null;
                cell = successor;
            }
            return null;
        }

        private static float ArmorMultiplier(int armor)
        {
            return armor >= 0 ? 1f - (0.06f * armor) / (1f + 0.06f * armor) : 2f - (float)Math.Pow(0.94, -armor);
        }
    }
}
