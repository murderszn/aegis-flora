using System;
using UnityEngine;
using AegisFlorae.Enemies;
using AegisFlorae.UI;

namespace AegisFlorae.Core
{
    public enum GamePhase { Build, Combat, Defeat, Victory }

    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Sanctum Vitality & Lives")]
        [SerializeField] private int maxLives = 20;
        [SerializeField] private int startingScrap = 100;

        public int CurrentLives { get; private set; }
        public int MaxLives => maxLives;
        public int CurrentScrap { get; private set; }
        public int CurrentWave { get; private set; } = 0;
        public int TotalLeaks { get; private set; } = 0;
        public GamePhase Phase { get; private set; } = GamePhase.Build;
        public bool IsGameOver => Phase == GamePhase.Defeat || Phase == GamePhase.Victory;

        [Header("Audio Feedback")]
        [SerializeField] private AudioClip leakSFX;
        [SerializeField] private AudioClip defeatSFX;

        // Events
        public static event Action<int, int> OnLivesChanged; // current, max
        public static event Action<int> OnScrapChanged;       // current
        public static event Action<int> OnWaveChanged;        // current
        public static event Action<CreepAgent, int> OnSanctumBreached;
        public static event Action OnDefeat;
        public static event Action OnVictory;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;

            CurrentLives = maxLives;
            CurrentScrap = startingScrap;
        }

        private void Start()
        {
            BroadcastState();
        }

        public void BroadcastState()
        {
            OnLivesChanged?.Invoke(CurrentLives, maxLives);
            OnScrapChanged?.Invoke(CurrentScrap);
            OnWaveChanged?.Invoke(CurrentWave);

            if (DotaHUDController.Instance != null)
            {
                DotaHUDController.Instance.UpdateHUD(CurrentLives, maxLives, CurrentScrap, CurrentWave);
            }
        }

        public void RegisterLeak(CreepAgent creep, int damage)
        {
            if (IsGameOver) return;

            int effectiveDamage = Mathf.Max(1, damage);
            CurrentLives = Mathf.Max(0, CurrentLives - effectiveDamage);
            TotalLeaks++;

            Debug.Log($"[Sanctum Breach] {creep.name} leaked! Took {effectiveDamage} damage. Lives remaining: {CurrentLives}/{maxLives}");

            if (leakSFX != null)
            {
                AudioSource.PlayClipAtPoint(leakSFX, transform.position);
            }

            OnSanctumBreached?.Invoke(creep, effectiveDamage);
            OnLivesChanged?.Invoke(CurrentLives, maxLives);

            if (DotaHUDController.Instance != null)
            {
                DotaHUDController.Instance.UpdateHUD(CurrentLives, maxLives, CurrentScrap, CurrentWave);
                DotaHUDController.Instance.TriggerSanctumDamageFlash();
            }

            if (CurrentLives <= 0)
            {
                TriggerDefeat();
            }
        }

        public void TriggerDefeat()
        {
            if (Phase == GamePhase.Defeat) return;

            Phase = GamePhase.Defeat;
            Debug.LogWarning("[Game Over] Sanctum has fallen! Defeat.");

            if (defeatSFX != null)
            {
                AudioSource.PlayClipAtPoint(defeatSFX, transform.position);
            }

            OnDefeat?.Invoke();

            if (DotaHUDController.Instance != null)
            {
                DotaHUDController.Instance.ShowDefeatScreen();
            }
        }

        public void AddScrap(int amount)
        {
            if (amount <= 0) return;
            CurrentScrap += amount;
            OnScrapChanged?.Invoke(CurrentScrap);

            if (DotaHUDController.Instance != null)
            {
                DotaHUDController.Instance.UpdateHUD(CurrentLives, maxLives, CurrentScrap, CurrentWave);
            }
        }

        public bool SpendScrap(int amount)
        {
            if (amount <= 0) return true;
            if (CurrentScrap < amount) return false;

            CurrentScrap -= amount;
            OnScrapChanged?.Invoke(CurrentScrap);

            if (DotaHUDController.Instance != null)
            {
                DotaHUDController.Instance.UpdateHUD(CurrentLives, maxLives, CurrentScrap, CurrentWave);
            }
            return true;
        }

        public void SetWave(int wave)
        {
            CurrentWave = wave;
            OnWaveChanged?.Invoke(CurrentWave);

            if (DotaHUDController.Instance != null)
            {
                DotaHUDController.Instance.UpdateHUD(CurrentLives, maxLives, CurrentScrap, CurrentWave);
            }
        }
    }
}
