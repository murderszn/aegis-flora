using System;
using System.Collections.Generic;
using AegisFlorae.Slice;

internal static class Program
{
    private static int assertions;

    private static void Main()
    {
        SharedFlowFieldUsesCardinalRoutes();
        PlacementAndSellingAreAtomic();
        ActiveWaypointCannotBeBlocked();
        AirUnitsIgnoreGroundMaze();
        GatlingRangeIncludesEnemyRadius();
        KillRewardsArePaidOnce();
        LeaksAreAppliedOnceAndDefeatStopsTheMatch();
        ThreeDemoWavesReachVictory();
        RestartRestoresInitialState();
        SteadyStateTickDoesNotAllocate();
        Console.WriteLine("Passed " + assertions + " behavioral assertions.");
    }

    private static void SharedFlowFieldUsesCardinalRoutes()
    {
        var sim = new SliceSimulation(7, 5, new GridCell(0, 2), new GridCell(6, 2));
        IReadOnlyList<GridCell> before = sim.GetPath(sim.Spawn);
        Equal(1, sim.FlowFieldRebuildCount, "first path request builds the shared field");
        sim.GetPath(sim.Spawn);
        Equal(1, sim.FlowFieldRebuildCount, "path previews reuse the shared field");
        Equal(7, before.Count, "open route uses shortest cardinal path");
        for (int i = 1; i < before.Count; i++)
            Equal(1, Math.Abs(before[i].X - before[i - 1].X) + Math.Abs(before[i].Y - before[i - 1].Y), "path does not use diagonals");

        Check(sim.TryPlaceTower(new GridCell(1, 2)), "legal route-changing placement succeeds");
        IReadOnlyList<GridCell> after = sim.GetPath(sim.Spawn);
        Check(after.Count > before.Count, "placement causes a longer route");
        for (int i = 0; i < after.Count; i++) Check(after[i] != new GridCell(1, 2), "flow field routes around tower");
        Check(sim.CanPlaceTower(new GridCell(2, 2)), "preview validates without committing");
        Equal(1, sim.Towers.Count, "placement preview has no side effects");
        Equal(2, sim.FlowFieldRebuildCount, "placement previews use a scratch field");
        Check(sim.TryPlaceTower(new GridCell(2, 2)), "second legal tower commits");
        Equal(3, sim.FlowFieldRebuildCount, "committed maze change rebuilds the shared field once");
        sim.GetPath(sim.Spawn);
        Equal(3, sim.FlowFieldRebuildCount, "route lookup reuses field after commit");
    }

    private static void PlacementAndSellingAreAtomic()
    {
        var sim = new SliceSimulation(5, 3, new GridCell(0, 1), new GridCell(4, 1), 100, 15);
        Check(!sim.TryPlaceTower(sim.Spawn), "spawn stays open");
        Check(!sim.TryPlaceTower(sim.Goal), "goal stays open");
        Check(!sim.TryPlaceTower(new GridCell(-1, 1)), "out-of-bounds placement fails");
        for (int x = 0; x < 5; x++)
        {
            Check(sim.TryPlaceTower(new GridCell(x, 0)), "upper row obstruction placement remains connected");
            Check(sim.TryPlaceTower(new GridCell(x, 2)), "lower row obstruction placement remains connected");
        }
        int scrapBeforeTrap = sim.Scrap;
        int towerCountBeforeTrap = sim.Towers.Count;
        Check(!sim.CanPlaceTower(new GridCell(2, 1)), "last corridor tile is rejected");
        Check(!sim.TryPlaceTower(new GridCell(2, 1)), "last corridor placement fails");
        Equal(scrapBeforeTrap, sim.Scrap, "failed trap placement charges no Scrap");
        Equal(towerCountBeforeTrap, sim.Towers.Count, "failed trap placement creates no tower");

        int id = sim.Towers[0].Id;
        int beforeSell = sim.Scrap;
        Check(sim.TrySellTower(id), "existing tower can be sold");
        Equal(beforeSell + 5, sim.Scrap, "sell refund rounds 75 percent of six Scrap like source");
        Check(!sim.TrySellTower(id), "same tower cannot be sold twice");
    }

    private static void ActiveWaypointCannotBeBlocked()
    {
        var sim = new SliceSimulation();
        Check(sim.StartNextWave(), "wave starts from prepare phase");
        sim.Tick(0.2f);
        EnemyState enemy = FirstAlive(sim);
        Check(enemy != null, "first Scout has spawned");
        Check(enemy.X > enemy.CurrentCell.X + 0.5f && enemy.X < enemy.TargetWaypoint.X + 0.5f,
            "enemy is between its current cell and target waypoint");
        string failure = sim.GetPlacementFailure(enemy.TargetWaypoint);
        Check(failure != null && failure.Contains("moving into"), "target waypoint reports an occupied move target");
        int scrap = sim.Scrap;
        Check(!sim.TryPlaceTower(enemy.TargetWaypoint), "tower cannot appear on an in-progress waypoint");
        Equal(scrap, sim.Scrap, "waypoint rejection is free");
        sim.Tick(0.25f);
        enemy = FirstAlive(sim);
        Check(enemy.CurrentCell.X > 0, "enemy advances to a non-spawn logical cell");
        string occupied = sim.GetPlacementFailure(enemy.CurrentCell);
        Check(occupied != null && occupied.Contains("occupies"), "last reached cell stays reserved during the next move");
    }

    private static void AirUnitsIgnoreGroundMaze()
    {
        var sim = new SliceSimulation(20, 10, new GridCell(0, 5), new GridCell(19, 5));
        Equal(2, sim.GetPath(sim.Spawn, true).Count, "air preview is a direct path independent of grid walls");
        Check(sim.TryPlaceTower(new GridCell(10, 0)), "tower can occupy an air route");
        Check(sim.StartNextWave(), "air test wave starts");
        RunUntilPhase(sim, SlicePhase.Preparing, 12f);
        Check(sim.StartNextWave(), "second wave includes air units");
        sim.Tick(5.0f);
        bool foundDrone = false;
        for (int i = 0; i < sim.Enemies.Count; i++)
        {
            EnemyState enemy = sim.Enemies[i];
            if (enemy.Kind != EnemyKind.Drone) continue;
            foundDrone = true;
            Check(enemy.IsAir, "Drone state identifies as air");
            Check(enemy.Y == 5.5f, "Drone follows straight spawn-to-goal line rather than ground detour");
        }
        Check(foundDrone, "wave 2 spawns a Drone");
    }

    private static void GatlingRangeIncludesEnemyRadius()
    {
        var sim = new SliceSimulation(8, 3, new GridCell(0, 1), new GridCell(7, 1), 20, 15, 1);
        Check(sim.TryPlaceTower(new GridCell(3, 1)), "range-edge tower builds");
        int shots = 0;
        bool resolvedLivePosition = false;
        sim.ShotFired += delegate(int towerId, int enemyId)
        {
            shots++;
            float x, y; bool isAir;
            resolvedLivePosition = sim.TryGetEnemyPosition(enemyId, out x, out y, out isAir)
                && !isAir && Math.Abs(x - 0.5f) < 0.0001f && Math.Abs(y - 1.5f) < 0.0001f;
        };
        Check(sim.StartNextWave(), "range-edge wave starts");
        sim.Tick(0.05f);
        Check(shots > 0, "source target range includes Scout radius beyond Gatling range");
        Check(resolvedLivePosition, "ShotFired can resolve a newly spawned target before the public view refreshes");
    }

    private static void KillRewardsArePaidOnce()
    {
        var sim = new SliceSimulation(7, 3, new GridCell(0, 1), new GridCell(6, 1), 20, 15, 1);
        Check(sim.TryPlaceTower(new GridCell(1, 0)), "Gatling build succeeds");
        int towerId = sim.Towers[0].Id;
        int shotCount = 0;
        sim.ShotFired += delegate(int firedTower, int target) { if (firedTower == towerId && target > 0) shotCount++; };
        Check(sim.StartNextWave(), "reward test wave starts");
        RunUntilPhase(sim, SlicePhase.Victory, 30f);
        Equal(1, sim.Towers.Count, "tower remains after the wave");
        Check(shotCount > 0, "Gatling emits targetable shot events");
        Equal(30, sim.Scrap, "all eight killed Scouts each pay their two-Scrap bounty once");
        Equal(15, sim.Lives, "near-spawn Gatling prevents Scout leaks");
    }

    private static void LeaksAreAppliedOnceAndDefeatStopsTheMatch()
    {
        var sim = new SliceSimulation(2, 1, new GridCell(0, 0), new GridCell(1, 0), 20, 2, 3);
        Check(sim.StartNextWave(), "defeat test wave starts");
        RunUntilPhase(sim, SlicePhase.Defeat, 20f);
        Equal(0, sim.Lives, "two goal arrivals defeat the two-life Sanctum without negative lives");
        Equal(SlicePhase.Defeat, sim.Phase, "last required leak enters defeat immediately");
        sim.Tick(10f);
        Equal(0, sim.Lives, "defeated match cannot apply another leak");
        Equal(0, sim.Enemies.Count, "leaked enemy is released from simulation state");
        sim.Tick(10f);
        Equal(0, sim.Enemies.Count, "terminal state stops remaining spawns");
        Check(!sim.StartNextWave(), "defeated match cannot start another wave");
    }

    private static void ThreeDemoWavesReachVictory()
    {
        var sim = new SliceSimulation(36, 20, new GridCell(0, 10), new GridCell(35, 10), 20, 100, 3);
        for (int wave = 1; wave <= 3; wave++)
        {
            Check(sim.StartNextWave(), "demo wave " + wave + " starts");
            RunUntilPhase(sim, wave == 3 ? SlicePhase.Victory : SlicePhase.Preparing, 60f);
            Equal(wave, sim.Wave, "completed wave counter advances");
        }
        Check(!sim.StartNextWave(), "victory prevents a fourth demo wave");
        Equal(3, sim.DemoWaveLimitValue, "short demo limit is explicit");
    }

    private static void RestartRestoresInitialState()
    {
        var sim = new SliceSimulation(6, 3, new GridCell(0, 1), new GridCell(5, 1), 20, 15, 1);
        Check(sim.TryPlaceTower(new GridCell(2, 0)), "restart test can place a tower");
        Check(sim.StartNextWave(), "restart test can start a wave");
        sim.Tick(0f);
        Equal(14, sim.Scrap, "zero elapsed time is a paused simulation step");
        sim.Restart();
        Equal(20, sim.Scrap, "restart restores starting Scrap");
        Equal(15, sim.Lives, "restart restores starting lives");
        Equal(0, sim.Wave, "restart resets wave number");
        Equal(0, sim.Towers.Count, "restart clears towers");
        Equal(0, sim.Enemies.Count, "restart clears enemies");
        Equal(SlicePhase.Preparing, sim.Phase, "restart returns to preparation");
    }

    private static void SteadyStateTickDoesNotAllocate()
    {
        var sim = new SliceSimulation();
        Check(sim.StartNextWave(), "allocation scenario starts a wave");
        sim.Tick(3.4f); // Spawn the full wave and grow render snapshots before measuring.
        Check(sim.Enemies.Count > 0, "allocation scenario has active enemies");
        sim.Tick(0.01f); sim.Tick(0.01f); // Warm JIT and view reuse paths.
        GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
        long before = GC.GetAllocatedBytesForCurrentThread();
        for (int i = 0; i < 30; i++) sim.Tick(0.01f);
        long allocated = GC.GetAllocatedBytesForCurrentThread() - before;
        Equal(0L, allocated, "steady-state Tick and render snapshots allocate no managed bytes");
    }

    private static EnemyState FirstAlive(SliceSimulation sim)
    {
        for (int i = 0; i < sim.Enemies.Count; i++) if (sim.Enemies[i].Alive) return sim.Enemies[i];
        return null;
    }

    private static void RunUntilPhase(SliceSimulation sim, SlicePhase target, float maxSeconds)
    {
        float elapsed = 0f;
        while (sim.Phase != target && elapsed < maxSeconds)
        {
            sim.Tick(0.05f);
            elapsed += 0.05f;
        }
        Equal(target, sim.Phase, "simulation reaches " + target + " before timeout");
    }

    private static void Check(bool value, string message)
    {
        assertions++;
        if (!value) throw new Exception("FAILED: " + message);
    }

    private static void Equal<T>(T expected, T actual, string message)
    {
        assertions++;
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
            throw new Exception("FAILED: " + message + " (expected " + expected + ", got " + actual + ")");
    }
}
