# Reachy 1 Controller and Simulator

## Experimental Branch Note

You are currently viewing the `experimental-animation-creator` branch.

### Purpose

This branch contains work-in-progress changes for:

- local JSON save/load for Animation Creator animations
- optional AI metadata on saved animations
- Emotion Reactions mapping from saved animations
- fallback logic back to default hardcoded emotions

### Open On A New Machine

```powershell
git clone <repo>
git fetch origin
git switch experimental-animation-creator
```

Then open the Unity project normally.

### Important Files

- `Assets/ReachyControlApp/Scripts/ReachyRuntimeControlUI.cs`
- `Assets/ReachyControlApp/LocalVoiceAgent/local_voice_agent_sidecar.py`

Generated or machine-local files should usually not be treated as the source of truth for this experiment:

- `Assets/ReachyControlApp/voice_agent_config.json`
- `Assets/ReachyControlApp/LocalVoiceAgent/local_voice_agent_sidecar_config.json`
- `Assets/ReachyControlApp/LocalVoiceAgent/local_voice_agent_sidecar_last_run.log`

### Animation JSON Location

Animation Creator saves local JSON animations under Unity's persistent data path in the `ReachyAnimations` folder.

On Windows this is typically:

```text
C:\Users\<YourUser>\AppData\LocalLow\Pollen Robotics\Reachy controller _ simulator\ReachyAnimations
```

A tracked example from development is included in this branch here:

- `ExperimentalSamples/ReachyAnimations/agree-test.json`

### Current Experimental Workflow

1. Open the Unity project from this branch.
2. Use the Animation Creator tab to create or import an animation.
3. Fill in:
   - `Pose title`
   - `Description`
   - `Suggested emotion key`
   - `Suggested AI use`
   - `Use this animation in AI Mode`
4. Press `Save locally`.
5. Select the saved animation.
6. Press `Create / Update Emotion Reaction`.

### Current Caveats

- This branch is a WIP and may be clunky or unstable.
- Unity play mode testing is still recommended before relying on this branch for demos or training.
- If `Use this animation in AI Mode` is disabled, Emotion Reactions should fall back to default hardcoded motions when a built-in fallback exists.
- Custom saved animations and local config state may differ across machines unless the required JSON files are recreated or shared.

### Recommended Branch Maintenance

- Keep implementation changes in this branch.
- Avoid committing machine-specific config/log churn unless it is intentionally part of the experiment.
- If `main` changes later, merge or rebase `main` into this branch when needed.
