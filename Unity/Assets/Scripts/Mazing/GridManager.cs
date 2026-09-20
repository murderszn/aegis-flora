using System;
using System.Collections.Generic;
using UnityEngine;

namespace AegisFlora.Mazing
{
    public class GridManager : MonoBehaviour
    {
        public static GridManager Instance { get; private set; }

        [Header("Grid Dimensions")]
        public int cols = 36;
        public int rows = 20;
        public float cellSize = 2.0f;
        public Vector3 gridOrigin = Vector3.zero;

        [Header("Key Portals")]
        public Vector2Int spawnCoords = new Vector2Int(0, 10);
        public Vector2Int sanctumCoords = new Vector2Int(35, 10);

        [Header("Layers & References")]
        public LayerMask groundLayer;
        public GameObject validGhostPrefab;
        public GameObject invalidGhostPrefab;

        private int[,] gridOccupancy; // 0 = empty, 1 = ruin, 2 = tower
        private GameObject currentGhost;
        private AStarPathfinder pathfinder;

        private void Awake()
        {
            if (Instance != null && Instance != this) Destroy(gameObject);
            else Instance = this;

            gridOccupancy = new int[cols, rows];
            pathfinder = new AStarPathfinder(cols, rows, spawnCoords, sanctumCoords);
        }

        public Vector3 GridToWorld(int gx, int gy, float yOffset = 0f)
        {
            return gridOrigin + new Vector3(gx * cellSize + cellSize * 0.5f, yOffset, gy * cellSize + cellSize * 0.5f);
        }

        public Vector2Int WorldToGrid(Vector3 worldPos)
        {
            Vector3 local = worldPos - gridOrigin;
            int gx = Mathf.FloorToInt(local.x / cellSize);
            int gy = Mathf.FloorToInt(local.z / cellSize);
            return new Vector2Int(gx, gy);
        }

        public bool InBounds(int gx, int gy)
        {
            return gx >= 0 && gx < cols && gy >= 0 && gy < rows;
        }

        public bool IsOccupied(int gx, int gy)
        {
            if (!InBounds(gx, gy)) return true;
            return gridOccupancy[gx, gy] != 0;
        }

        public bool CanPlaceTower(int gx, int gy)
        {
            if (!InBounds(gx, gy)) return false;
            if (gx == spawnCoords.x && gy == spawnCoords.y) return false;
            if (gx == sanctumCoords.x && gy == sanctumCoords.y) return false;
            if (gridOccupancy[gx, gy] != 0) return false;

            // Speculative maze path validation
            return pathfinder.ValidateMazeWithBlock(gridOccupancy, gx, gy);
        }

        public bool PlaceTower(int gx, int gy, GameObject towerPrefab)
        {
            if (!CanPlaceTower(gx, gy)) return false;

            gridOccupancy[gx, gy] = 2;
            Vector3 worldPos = GridToWorld(gx, gy);
            GameObject tower = Instantiate(towerPrefab, worldPos, Quaternion.identity, transform);
            
            // Notify active creeps to recalculate their paths
            OnMazeModified?.Invoke();
            return true;
        }

        public void RemoveTower(int gx, int gy)
        {
            if (InBounds(gx, gy) && gridOccupancy[gx, gy] == 2)
            {
                gridOccupancy[gx, gy] = 0;
                OnMazeModified?.Invoke();
            }
        }

        public List<Vector2Int> GetCurrentShortestPath(Vector2Int start)
        {
            return pathfinder.FindPath(gridOccupancy, start, sanctumCoords);
        }

        public event Action OnMazeModified;
    }
}
