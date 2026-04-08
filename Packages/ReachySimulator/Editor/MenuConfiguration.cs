using UnityEditor;

#if UNITY_EDITOR
public static class MenuConfiguration
{
    [MenuItem("Pollen Robotics/Validate GRPC Dependencies")]
    private static void ValidateGrpcDependencies()
    {
        GrpcDependencyUtility.ValidateBundledGrpcDependencies(interactive: true);
    }
}
#endif
