using System;
using System.Collections.Generic;
using UnityEngine;
using AegisFlora.Mazing;
using AegisFlora.Core;

namespace AegisFlora.Enemies
{
    public enum DamageType { Kinetic, Explosive, Energy, Sonic }

    public class CreepAgent : MonoBehaviour
    {
        [Header("Stats")]
        public float maxHealth = 100f;
        public float currentHealth;
        public float baseMoveSpeed = 3.5f;
        public int scrapBounty = 8;
        public int sanctumDamage = 1;
        public bool isArmored = false;
        public bool isAirUnit = false;

        [Header("Visual Feedback & Shaders")]
        public Renderer meshRenderer;
        public GameObject deathExplosionPrefab;
        public Transform healthBarForeground;

        [Header("Sanctum Breach & Leak")]
        public GameObject breachVFXPrefab;
        public AudioClip breachSFX;

        public static event Action<CreepAgent, int> OnCreepSanctumBreached;

        private List<Vector2Int> currentPath;
        private int currentWaypointIndex = 0;
        private float slowTimer = 0f;
        private float slowFactor = 1f;
        private MaterialPropertyBlock propBlock;

        public bool IsAlive => currentHealth > 0;

        private void Awake()
        {
            currentHealth = maxHealth;
            propBlock = new MaterialPropertyBlock();
        }

        private void Start()
        {
            if (GridManager.Instance != null)
            {
                GridManager.Instance.OnMazeModified += RecalculatePath;
                RecalculatePath();
            }
        }

        private void OnDestroy()
        {
            if (GridManager.Instance != null)
            {
                GridManager.Instance.OnMazeModified -= RecalculatePath;
            }
        }

        public void RecalculatePath()
        {
            if (isAirUnit || GridManager.Instance == null) return;
            Vector2Int myGrid = GridManager.Instance.WorldToGrid(transform.position);
            currentPath = GridManager.Instance.GetCurrentShortestPath(myGrid);
            currentWaypointIndex = 0;
        }

        private void Update()
        {
            if (!IsAlive) return;

            // Handle Slow Timer
            if (slowTimer > 0f)
            {
                slowTimer -= Time.deltaTime;
                if (slowTimer <= 0f) slowFactor = 1f;
            }

            MoveAlongPath();
        }

        private void MoveAlongPath()
        {
            float speed = baseMoveSpeed * slowFactor;
            Vector3 targetWorld;

            if (isAirUnit || currentPath == null || currentWaypointIndex >= currentPath.Count)
            {
                // Move straight to sanctum
                targetWorld = GridManager.Instance.GridToWorld(GridManager.Instance.sanctumCoords.x, GridManager.Instance.sanctumCoords.y, transform.position.y);
            }
            else
            {
                Vector2Int wp = currentPath[currentWaypointIndex];
                targetWorld = GridManager.Instance.GridToWorld(wp.x, wp.y, transform.position.y);
            }

            Vector3 moveDir = targetWorld - transform.position;
            moveDir.y = 0;
            float dist = moveDir.magnitude;

            if (dist < 0.1f)
            {
                currentWaypointIndex++;
                if (currentWaypointIndex >= currentPath.Count)
                {
                    ReachSanctum();
                    return;
                }
            }
            else
            {
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(moveDir), Time.deltaTime * 10f);
                transform.position += moveDir.normalized * (speed * Time.deltaTime);
            }
        }

        public void TakeDamage(float amount, DamageType type)
        {
            if (!IsAlive) return;

            // Armor mitigation (Dota 2 style calculation)
            if (isArmored && type == DamageType.Kinetic) amount *= 0.6f;
            if (type == DamageType.Energy) amount *= 1.25f; // Energy shreds armor

            currentHealth -= amount;
            UpdateHealthBar();
            FlashWhite();

            if (currentHealth <= 0f)
            {
                Die();
            }
        }

        public void ApplySlow(float slowPercent, float duration)
        {
            slowFactor = Mathf.Min(slowFactor, 1f - slowPercent);
            slowTimer = Mathf.Max(slowTimer, duration);
        }

        public float GetPathProgress()
        {
            return currentWaypointIndex + (1f / (Vector3.Distance(transform.position, GridManager.Instance.GridToWorld(GridManager.Instance.sanctumCoords.x, GridManager.Instance.sanctumCoords.y)) + 1f));
        }

        private void FlashWhite()
        {
            if (meshRenderer != null)
            {
                meshRenderer.GetPropertyBlock(propBlock);
                propBlock.SetFloat("_HitFlash", 1.0f);
                meshRenderer.SetPropertyBlock(propBlock);
                Invoke(nameof(ResetFlash), 0.08f);
            }
        }

        private void ResetFlash()
        {
            if (meshRenderer != null)
            {
                meshRenderer.GetPropertyBlock(propBlock);
                propBlock.SetFloat("_HitFlash", 0.0f);
                meshRenderer.SetPropertyBlock(propBlock);
            }
        }

        private void UpdateHealthBar()
        {
            if (healthBarForeground != null)
            {
                float ratio = Mathf.Clamp01(currentHealth / maxHealth);
                healthBarForeground.localScale = new Vector3(ratio, 1f, 1f);
            }
        }

        private void ReachSanctum()
        {
            // 1. Fire static breach event
            OnCreepSanctumBreached?.Invoke(this, sanctumDamage);

            // 2. Play breach visual effects
            if (breachVFXPrefab != null)
            {
                Instantiate(breachVFXPrefab, transform.position, Quaternion.identity);
            }
            else if (deathExplosionPrefab != null)
            {
                Instantiate(deathExplosionPrefab, transform.position, Quaternion.identity);
            }

            // 3. Play breach audio
            if (breachSFX != null)
            {
                AudioSource.PlayClipAtPoint(breachSFX, transform.position);
            }

            // 4. Notify centralized GameManager to decrement lives and trigger defeat if lives <= 0
            if (GameManager.Instance != null)
            {
                GameManager.Instance.RegisterLeak(this, sanctumDamage);
            }

            // 5. Destroy creep agent
            Destroy(gameObject);
        }

        private void Die()
        {
            if (deathExplosionPrefab != null)
            {
                Instantiate(deathExplosionPrefab, transform.position, Quaternion.identity);
            }
            Destroy(gameObject);
        }
    }
}
