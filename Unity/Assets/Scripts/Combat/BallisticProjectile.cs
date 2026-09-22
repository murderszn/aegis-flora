using UnityEngine;
using AegisFlorae.Enemies;

namespace AegisFlorae.Combat
{
    public class BallisticProjectile : MonoBehaviour
    {
        public float arcHeight = 5.0f;
        public float flightDuration = 0.85f;
        public GameObject explosionVFX;

        private Vector3 startPos;
        private Vector3 targetPos;
        private float damage;
        private float splashRadius;
        private float elapsedTime = 0f;

        public void Initialize(Vector3 start, Vector3 target, float dmg, float radius)
        {
            this.startPos = start;
            this.targetPos = target;
            this.damage = dmg;
            this.splashRadius = radius;
            transform.position = start;
        }

        private void Update()
        {
            elapsedTime += Time.deltaTime;
            float t = Mathf.Clamp01(elapsedTime / flightDuration);

            // Parabolic Arc Formula: y(t) = 4 * h * t * (1 - t)
            Vector3 linearPos = Vector3.Lerp(startPos, targetPos, t);
            linearPos.y += 4f * arcHeight * t * (1f - t);
            transform.position = linearPos;

            // Face direction of travel
            Vector3 velocity = (targetPos - startPos) / flightDuration + Vector3.up * (4f * arcHeight * (1f - 2f * t));
            if (velocity.sqrMagnitude > 0.001f)
            {
                transform.rotation = Quaternion.LookRotation(velocity);
            }

            if (t >= 1.0f)
            {
                Detonate();
            }
        }

        private void Detonate()
        {
            if (explosionVFX != null)
            {
                Instantiate(explosionVFX, transform.position, Quaternion.identity);
            }

            // Splash AoE damage
            Collider[] hits = Physics.OverlapSphere(transform.position, splashRadius);
            foreach (var col in hits)
            {
                var creep = col.GetComponent<CreepAgent>();
                if (creep != null && creep.IsAlive)
                {
                    creep.TakeDamage(damage, DamageType.Explosive);
                }
            }

            Destroy(gameObject);
        }
    }
}
