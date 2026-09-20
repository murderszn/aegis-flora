using UnityEngine;
using AegisFlora.Enemies;

namespace AegisFlora.Towers
{
    public enum TowerType { PetalGatling, BloomMortar, PrismPillar, ResonanceObelisk }

    public class TowerController : MonoBehaviour
    {
        [Header("Tower Identity & Stats")]
        public TowerType towerType;
        public string towerName = "Defense Tower";
        public float baseRange = 6f;
        public float baseDamage = 15f;
        public float fireRate = 3f; // Attacks per second

        [Header("3D Animation Transforms")]
        public Transform turretTurnTable;
        public Transform barrelCluster;
        public Transform muzzlePoint;
        public LineRenderer beamLineRenderer;
        public ParticleSystem muzzleFlash;
        public ParticleSystem shellEjection;

        [Header("Projectile Prefabs")]
        public GameObject projectilePrefab;
        public GameObject impactEffectPrefab;

        private float fireCooldown = 0f;
        private CreepAgent currentTarget = null;
        private float beamChargeTime = 0f;

        private void Update()
        {
            AcquireTarget();

            if (currentTarget != null)
            {
                AimTurret(currentTarget.transform.position);

                switch (towerType)
                {
                    case TowerType.PetalGatling:
                        HandleGatlingCombat();
                        break;
                    case TowerType.BloomMortar:
                        HandleMortarCombat();
                        break;
                    case TowerType.PrismPillar:
                        HandleBeamCombat();
                        break;
                    case TowerType.ResonanceObelisk:
                        HandleResonancePulse();
                        break;
                }
            }
            else
            {
                if (beamLineRenderer != null) beamLineRenderer.enabled = false;
                beamChargeTime = 0f;
            }
        }

        private void AimTurret(Vector3 targetPos)
        {
            if (turretTurnTable == null) return;
            Vector3 dir = targetPos - turretTurnTable.position;
            dir.y = 0; // Rotate horizontally on Y-axis
            if (dir.sqrMagnitude > 0.001f)
            {
                Quaternion targetRot = Quaternion.LookRotation(dir);
                turretTurnTable.rotation = Quaternion.Slerp(turretTurnTable.rotation, targetRot, Time.deltaTime * 12f);
            }
        }

        private void HandleGatlingCombat()
        {
            fireCooldown -= Time.deltaTime;
            // Rotate Gatling barrels continuously while firing
            if (barrelCluster != null)
            {
                barrelCluster.Rotate(Vector3.forward, 720f * Time.deltaTime, Space.Self);
            }

            if (fireCooldown <= 0f)
            {
                fireCooldown = 1f / fireRate;
                if (muzzleFlash != null) muzzleFlash.Play();
                if (shellEjection != null) shellEjection.Play();

                currentTarget.TakeDamage(baseDamage, DamageType.Kinetic);
            }
        }

        private void HandleMortarCombat()
        {
            fireCooldown -= Time.deltaTime;
            if (fireCooldown <= 0f)
            {
                fireCooldown = 1f / fireRate;
                if (muzzleFlash != null) muzzleFlash.Play();

                if (projectilePrefab != null && muzzlePoint != null)
                {
                    GameObject shell = Instantiate(projectilePrefab, muzzlePoint.position, Quaternion.identity);
                    var ballistic = shell.GetComponent<Combat.BallisticProjectile>();
                    if (ballistic != null)
                    {
                        ballistic.Initialize(muzzlePoint.position, currentTarget.transform.position, baseDamage, 3.5f);
                    }
                }
            }
        }

        private void HandleBeamCombat()
        {
            if (beamLineRenderer != null && muzzlePoint != null)
            {
                beamLineRenderer.enabled = true;
                beamLineRenderer.SetPosition(0, muzzlePoint.position);
                beamLineRenderer.SetPosition(1, currentTarget.transform.position + Vector3.up * 0.5f);
            }

            beamChargeTime += Time.deltaTime;
            float rampMultiplier = 1f + Mathf.Min(3.0f, beamChargeTime * 0.8f);
            float dealDmg = baseDamage * rampMultiplier * Time.deltaTime;
            currentTarget.TakeDamage(dealDmg, DamageType.Energy);
        }

        private void HandleResonancePulse()
        {
            fireCooldown -= Time.deltaTime;
            if (fireCooldown <= 0f)
            {
                fireCooldown = 1f / fireRate;
                if (impactEffectPrefab != null)
                {
                    Instantiate(impactEffectPrefab, transform.position, Quaternion.identity);
                }
                
                Collider[] hits = Physics.OverlapSphere(transform.position, baseRange);
                foreach (var col in hits)
                {
                    var creep = col.GetComponent<CreepAgent>();
                    if (creep != null)
                    {
                        creep.ApplySlow(0.4f, 1.8f);
                        creep.TakeDamage(baseDamage, DamageType.Sonic);
                    }
                }
            }
        }

        private void AcquireTarget()
        {
            if (currentTarget != null && (!currentTarget.IsAlive || Vector3.Distance(transform.position, currentTarget.transform.position) > baseRange))
            {
                currentTarget = null;
            }

            if (currentTarget == null)
            {
                Collider[] hits = Physics.OverlapSphere(transform.position, baseRange);
                float bestProgress = -1f;

                foreach (var col in hits)
                {
                    var creep = col.GetComponent<CreepAgent>();
                    if (creep != null && creep.IsAlive)
                    {
                        float prog = creep.GetPathProgress();
                        if (prog > bestProgress)
                        {
                            bestProgress = prog;
                            currentTarget = creep;
                        }
                    }
                }
            }
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireSphere(transform.position, baseRange);
        }
    }
}
