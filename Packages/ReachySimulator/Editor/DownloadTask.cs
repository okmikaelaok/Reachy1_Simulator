using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;

#if UNITY_EDITOR
internal static class GrpcDependencyUtility
{
    private const string MissingDependenciesWarningKey = "ReachySimulator.MissingGrpcDependenciesWarningShown";

    private static readonly string[] RequiredDependencyPaths =
    {
        @"Assets/Plugins/Google.Protobuf/lib/net45/Google.Protobuf.dll",
        @"Assets/Plugins/Grpc.Core.Api/lib/net45/Grpc.Core.Api.dll",
        @"Assets/Plugins/Grpc.Core/lib/net45/Grpc.Core.dll",
        @"Assets/Plugins/System.Buffers/lib/net45/System.Buffers.dll",
        @"Assets/Plugins/System.Memory/lib/net45/System.Memory.dll",
        @"Assets/Plugins/System.Runtime.CompilerServices.Unsafe/lib/net45/System.Runtime.CompilerServices.Unsafe.dll",
        @"Assets/Plugins/Grpc.Core/runtimes/win/x64/grpc_csharp_ext.dll"
    };

    [InitializeOnLoadMethod]
    private static void ValidateBundledGrpcDependenciesOnLoad()
    {
        EditorApplication.delayCall += () =>
        {
            if (Application.isBatchMode || EditorApplication.isCompiling || EditorApplication.isUpdating)
            {
                return;
            }

            ValidateBundledGrpcDependencies(interactive: false);
        };
    }

    public static bool ValidateBundledGrpcDependencies(bool interactive)
    {
        string[] missingPaths = GetMissingDependencyPaths();
        if (missingPaths.Length == 0)
        {
            if (interactive)
            {
                Debug.Log("ReachySimulator GRPC dependency check passed. Bundled plugins are present under Assets/Plugins.");
            }

            return true;
        }

        string message = BuildMissingDependenciesMessage(missingPaths);

        if (!SessionState.GetBool(MissingDependenciesWarningKey, false))
        {
            Debug.LogError(message);
            SessionState.SetBool(MissingDependenciesWarningKey, true);
        }

        if (interactive)
        {
            EditorUtility.DisplayDialog("ReachySimulator GRPC dependencies missing", message, "OK");
        }

        return false;
    }

    private static string[] GetMissingDependencyPaths()
    {
        string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
        List<string> missingPaths = new List<string>();

        foreach (string relativePath in RequiredDependencyPaths)
        {
            string fullPath = Path.Combine(projectRoot, relativePath);
            if (!File.Exists(fullPath))
            {
                missingPaths.Add(relativePath.Replace('\\', '/'));
            }
        }

        return missingPaths.ToArray();
    }

    private static string BuildMissingDependenciesMessage(string[] missingPaths)
    {
        StringBuilder builder = new StringBuilder();
        builder.AppendLine("ReachySimulator is missing bundled GRPC/Protobuf plugin files.");
        builder.AppendLine("A clean checkout of this repository should already include them under Assets/Plugins.");
        builder.AppendLine("Missing files:");

        foreach (string missingPath in missingPaths)
        {
            builder.AppendLine("- " + missingPath);
        }

        builder.AppendLine("If this came from GitHub, the checkout is incomplete or the plugin binaries were not committed.");
        return builder.ToString();
    }
}
#endif
