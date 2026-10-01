using UnityEngine;
using UnityEngine.SceneManagement;

namespace AegisFlorae
{
    /// <summary>Boot redirects the player to the interactive courtyard slice.</summary>
    public sealed class AegisBootSceneLoader : MonoBehaviour
    {
        private void Awake()
        {
            if (SceneManager.GetActiveScene().name == "Boot")
                SceneManager.LoadScene("SanctuaryCourtyard", LoadSceneMode.Single);
        }
    }
}
