using System;
using System.Collections.Generic;
using UnityEngine;

namespace AegisFlora.Mazing
{
    public class AStarPathfinder
    {
        private readonly int width;
        private readonly int height;
        private readonly Vector2Int defaultSpawn;
        private readonly Vector2Int sanctumGoal;

        private static readonly Vector2Int[] Directions = new Vector2Int[]
        {
            new Vector2Int(1, 0),
            new Vector2Int(-1, 0),
            new Vector2Int(0, 1),
            new Vector2Int(0, -1)
        };

        public AStarPathfinder(int width, int height, Vector2Int spawn, Vector2Int goal)
        {
            this.width = width;
            this.height = height;
            this.defaultSpawn = spawn;
            this.sanctumGoal = goal;
        }

        public bool ValidateMazeWithBlock(int[,] currentGrid, int testX, int testY)
        {
            // Temporarily block test cell
            currentGrid[testX, testY] = 2;
            
            // Check path from spawn to goal
            List<Vector2Int> path = FindPath(currentGrid, defaultSpawn, sanctumGoal);
            
            // Revert cell
            currentGrid[testX, testY] = 0;

            return path != null && path.Count > 0;
        }

        public List<Vector2Int> FindPath(int[,] grid, Vector2Int start, Vector2Int goal)
        {
            if (start.x < 0 || start.x >= width || start.y < 0 || start.y >= height) return null;
            if (goal.x < 0 || goal.x >= width || goal.y < 0 || goal.y >= height) return null;
            if (grid[start.x, start.y] != 0 || grid[goal.x, goal.y] != 0) return null;

            int totalNodes = width * height;
            float[] gScore = new float[totalNodes];
            int[] cameFrom = new int[totalNodes];
            bool[] closed = new bool[totalNodes];

            for (int i = 0; i < totalNodes; i++)
            {
                gScore[i] = float.PositiveInfinity;
                cameFrom[i] = -1;
            }

            int startIndex = ToIndex(start.x, start.y);
            int goalIndex = ToIndex(goal.x, goal.y);
            gScore[startIndex] = 0f;

            // Simple min-heap / priority queue
            var openList = new List<NodeCost>();
            openList.Add(new NodeCost(startIndex, Heuristic(start, goal)));

            while (openList.Count > 0)
            {
                openList.Sort((a, b) => a.fScore.CompareTo(b.fScore));
                NodeCost current = openList[0];
                openList.RemoveAt(0);

                int currIndex = current.index;
                if (closed[currIndex]) continue;
                closed[currIndex] = true;

                if (currIndex == goalIndex)
                {
                    return ReconstructPath(cameFrom, goalIndex);
                }

                int cx = currIndex % width;
                int cy = currIndex / width;

                foreach (var dir in Directions)
                {
                    int nx = cx + dir.x;
                    int ny = cy + dir.y;

                    if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
                    int neighborIndex = ToIndex(nx, ny);

                    if (grid[nx, ny] != 0 || closed[neighborIndex]) continue;

                    float tentativeG = gScore[currIndex] + 1f;
                    if (tentativeG < gScore[neighborIndex])
                    {
                        cameFrom[neighborIndex] = currIndex;
                        gScore[neighborIndex] = tentativeG;
                        float f = tentativeG + Heuristic(new Vector2Int(nx, ny), goal);
                        openList.Add(new NodeCost(neighborIndex, f));
                    }
                }
            }

            return null; // No open path found!
        }

        private int ToIndex(int x, int y) => y * width + x;

        private float Heuristic(Vector2Int a, Vector2Int b)
        {
            return Mathf.Abs(a.x - b.x) + Mathf.Abs(a.y - b.y);
        }

        private List<Vector2Int> ReconstructPath(int[] cameFrom, int current)
        {
            var path = new List<Vector2Int>();
            while (current != -1)
            {
                path.Add(new Vector2Int(current % width, current / width));
                current = cameFrom[current];
            }
            path.Reverse();
            return path;
        }

        private struct NodeCost
        {
            public int index;
            public float fScore;
            public NodeCost(int idx, float f) { index = idx; fScore = f; }
        }
    }
}
