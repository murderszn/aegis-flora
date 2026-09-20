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
            if (GridManager.Instance == null) return;

            float speed = baseMoveSpeed * slowFactor;

            // 1. Air Units: fly straight toward the Sanctum ignoring grid maze barriers
            if (isAirUnit)
            {
                Vector3 sanctumPos = GridManager.Instance.GridToWorld(GridManager.Instance.sanctumCoords.x, GridManager.Instance.sanctumCoords.y, transform.position.y);
                Vector3 airDir = sanctumPos - transform.position;
                airDir.y = 0f;
                float airDist = airDir.magnitude;

                if (airDist < 0.15f)
                {
                    ReachSanctum();
                    return;
                }

                if (airDir.sqrMagnitude > 0.0001f)
                {
                    transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(airDir), Time.deltaTime * 10f);
                    transform.position += airDir.normalized * (speed * Time.deltaTime);
                }
                return;
            }

            // 2. Ground Units: require valid maze path
            if (currentPath == null || currentPath.Count == 0)
            {
                RecalculatePath();
                if (currentPath == null || currentPath.Count == 0)
                {
                    // No path available: wait safely instead of clipping through maze walls or throwing null references
                    return;
                }
            }

            if (currentWaypointIndex >= currentPath.Count)
            {
                ReachSanctum();
                return;
            }

            Vector2Int currentWp = currentPath[currentWaypointIndex];
            Vector3 targetWorld = GridManager.Instance.GridToWorld(currentWp.x, currentWp.y, transform.position.y);
            Vector3 moveDir = targetWorld - transform.position;
            moveDir.y = 0f;
            float dist = moveDir.magnitude;

            if (dist < 0.15f)
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
                if (moveDir.sqrMagnitude > 0.0001f)
                {
                    transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(moveDir), Time.deltaTime * 10f);
                    transform.position += moveDir.normalized * (speed * Time.deltaTime);
                }
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
            if (GridManager.Instance == null) return 0f;

            Vector3 sanctumPos = GridManager.Instance.GridToWorld(GridManager.Instance.sanctumCoords.x, GridManager.Instance.sanctumCoords.y, transform.position.y);
            float distToSanctum = Vector3.Distance(transform.position, sanctumPos);

            if (isAirUnit || currentPath == null || currentPath.Count == 0)
            {
                Vector3 spawnPos = GridManager.Instance.GridToWorld(GridManager.Instance.spawnCoords.x, GridManager.Instance.spawnCoords.y, transform.position.y);
                float totalDist = Vector3.Distance(spawnPos, sanctumPos);
                if (totalDist > 0.001f)
                {
                    return Mathf.Clamp01(1f - (distToSanctum / totalDist));
                }
                return 1f / (distToSanctum + 1f);
            }

            return currentWaypointIndex + (1f / (distToSanctum + 1f));
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
