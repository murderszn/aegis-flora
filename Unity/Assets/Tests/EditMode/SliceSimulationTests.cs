using AegisFlorae.Slice;
using NUnit.Framework;

namespace AegisFlorae.Tests
{
    public class SliceSimulationTests
    {
        [Test]
        public void PlacementThatSealsRouteDoesNotSpendScrap()
        {
            var simulation = new SliceSimulation(3, 1, startingScrap: 20);
            Assert.That(simulation.TryPlaceTower(new GridCell(1, 0)), Is.False);
            Assert.That(simulation.Scrap, Is.EqualTo(20));
            Assert.That(simulation.Towers.Count, Is.Zero);
            Assert.That(simulation.GetPath(simulation.Spawn).Count, Is.EqualTo(3));
        }

        [Test]
        public void SaleRoundsRefundLikeBrowserGame()
        {
            var simulation = new SliceSimulation();
            Assert.That(simulation.TryPlaceTower(new GridCell(2, 9)), Is.True);
            int id = simulation.Towers[0].Id;
            Assert.That(simulation.Scrap, Is.EqualTo(14));
            Assert.That(simulation.TrySellTower(id), Is.True);
            Assert.That(simulation.Scrap, Is.EqualTo(19));
            Assert.That(simulation.TrySellTower(id), Is.False);
            Assert.That(simulation.Scrap, Is.EqualTo(19));
        }

        [Test]
        public void ZeroStepFreezesWaveAndRestartResetsState()
        {
            var simulation = new SliceSimulation();
            Assert.That(simulation.StartNextWave(), Is.True);
            simulation.Tick(.2f);
            float x = simulation.Enemies[0].X;
            simulation.Tick(0);
            Assert.That(simulation.Enemies[0].X, Is.EqualTo(x));
            simulation.Restart();
            Assert.That(simulation.Phase, Is.EqualTo(SlicePhase.Preparing));
            Assert.That(simulation.Scrap, Is.EqualTo(20));
            Assert.That(simulation.Lives, Is.EqualTo(15));
            Assert.That(simulation.Wave, Is.Zero);
            Assert.That(simulation.Enemies.Count, Is.Zero);
        }

        [Test]
        public void GroundEnemyDestinationCannotBeBlockedMidStep()
        {
            var simulation = new SliceSimulation();
            simulation.StartNextWave();
            simulation.Tick(.1f);
            var enemy = simulation.Enemies[0];
            int scrap = simulation.Scrap;
            Assert.That(simulation.TryPlaceTower(enemy.TargetWaypoint), Is.False);
            Assert.That(simulation.Scrap, Is.EqualTo(scrap));
        }
    }
}
