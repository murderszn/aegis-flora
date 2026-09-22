using UnityEngine;
using UnityEngine.UI;
using AegisFlorae.Mazing;

namespace AegisFlorae.UI
{
    public class DotaHUDController : MonoBehaviour
    {
        public static DotaHUDController Instance { get; private set; }

        [Header("Resource & Vitality Readouts")]
        public Text livesText;
        public Text scrapText;
        public Text waveText;
        public Slider sanctumHealthBar;

        [Header("Defeat & Feedback Screens")]
        public GameObject defeatScreen;
        public Image sanctumDamageVignette;

        [Header("Tower Build Dock Buttons")]
        public Button btnGatling;  // Q
        public Button btnMortar;   // W
        public Button btnPrism;    // E
        public Button btnResonance;// R

        [Header("Prefabs for Placement")]
        public GameObject gatlingPrefab;
        public GameObject mortarPrefab;
        public GameObject prismPrefab;
        public GameObject resonancePrefab;

        private GameObject selectedTowerPrefab = null;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        public void UpdateHUD(int lives, int maxLives, int scrap, int wave)
        {
            if (livesText != null) livesText.text = lives.ToString();
            if (scrapText != null) scrapText.text = scrap.ToString();
            if (waveText != null) waveText.text = $"Wave {wave}";
            if (sanctumHealthBar != null && maxLives > 0)
            {
                sanctumHealthBar.value = Mathf.Clamp01((float)lives / maxLives);
            }
        }

        public void TriggerSanctumDamageFlash()
        {
            if (sanctumDamageVignette != null)
            {
                sanctumDamageVignette.color = new Color(1f, 0f, 0f, 0.4f);
                CancelInvoke(nameof(ResetDamageFlash));
                Invoke(nameof(ResetDamageFlash), 0.25f);
            }
        }

        private void ResetDamageFlash()
        {
            if (sanctumDamageVignette != null)
            {
                sanctumDamageVignette.color = new Color(1f, 0f, 0f, 0f);
            }
        }

        public void ShowDefeatScreen()
        {
            if (defeatScreen != null)
            {
                defeatScreen.SetActive(true);
            }
        }

        private void Update()
        {
            HandleHotkeys();
            HandlePlacementInput();
        }

        private void HandleHotkeys()
        {
            if (Input.GetKeyDown(KeyCode.Q) || Input.GetKeyDown(KeyCode.Alpha1)) SelectTower(gatlingPrefab);
            if (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.Alpha2)) SelectTower(mortarPrefab);
            if (Input.GetKeyDown(KeyCode.E) || Input.GetKeyDown(KeyCode.Alpha3)) SelectTower(prismPrefab);
            if (Input.GetKeyDown(KeyCode.R) || Input.GetKeyDown(KeyCode.Alpha4)) SelectTower(resonancePrefab);
            if (Input.GetKeyDown(KeyCode.Escape)) Deselect();
        }

        public void SelectTower(GameObject prefab)
        {
            selectedTowerPrefab = prefab;
        }

        public void Deselect()
        {
            selectedTowerPrefab = null;
        }

        private void HandlePlacementInput()
        {
            if (selectedTowerPrefab == null) return;

            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            if (Physics.Raycast(ray, out RaycastHit hit, 100f, GridManager.Instance.groundLayer))
            {
                Vector2Int gridPos = GridManager.Instance.WorldToGrid(hit.point);

                if (Input.GetMouseButtonDown(0))
                {
                    bool success = GridManager.Instance.PlaceTower(gridPos.x, gridPos.y, selectedTowerPrefab);
                    if (success)
                    {
                        // Placed successfully!
                    }
                }
                else if (Input.GetMouseButtonDown(1))
                {
                    Deselect();
                }
            }
        }
    }
}
