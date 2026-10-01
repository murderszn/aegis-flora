using System.Collections;
using AegisFlorae.Slice;
using NUnit.Framework;
using TMPro;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.UI;

namespace AegisFlorae.Tests
{
    public class SanctuarySliceTests
    {
        [UnityTest]
        public IEnumerator CourtyardStartsAndHudControlsWavePauseAndRestart()
        {
            var root = new GameObject("Slice under test");
            var slice = root.AddComponent<SanctuarySlice>();
            yield return null;
            yield return null;
            Assert.That(slice.Simulation, Is.Not.Null);
            Assert.That(root.GetComponentInChildren<Camera>(), Is.Not.Null);
            Assert.That(root.GetComponentInChildren<Canvas>(), Is.Not.Null);
            Assert.That(root.GetComponentsInChildren<TextMeshProUGUI>().Length, Is.GreaterThan(5));

            FindButton(root, "CALL WAVE").onClick.Invoke();
            yield return null;
            Assert.That(slice.Simulation.Phase, Is.EqualTo(SlicePhase.Combat));
            Assert.That(slice.Simulation.Wave, Is.EqualTo(1));

            FindButton(root, "PAUSE").onClick.Invoke();
            yield return null;
            Assert.That(slice.IsPaused, Is.True);
            int enemies = slice.Simulation.Enemies.Count;
            if (enemies > 0)
            {
                float x = slice.Simulation.Enemies[0].X;
                yield return new WaitForSecondsRealtime(.12f);
                Assert.That(slice.Simulation.Enemies[0].X, Is.EqualTo(x));
            }
            FindButton(root, "RESTART").onClick.Invoke();
            yield return null;
            Assert.That(slice.IsPaused, Is.False);
            Assert.That(slice.Simulation.Wave, Is.Zero);
            Assert.That(slice.Simulation.Scrap, Is.EqualTo(20));
            Object.Destroy(root);
            yield return null;
            LogAssert.NoUnexpectedReceived();
        }

        private static Button FindButton(GameObject root, string prefix)
        {
            foreach (var button in root.GetComponentsInChildren<Button>())
                if (button.name.StartsWith(prefix)) return button;
            Assert.Fail("Missing HUD control: " + prefix);
            return null;
        }
    }
}
