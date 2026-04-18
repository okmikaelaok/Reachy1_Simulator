# Experimental Animation Creator Setup

This note is for the `experimental-animation-creator` branch.

## Purpose

This branch contains work-in-progress changes for:

- local JSON save/load for Animation Creator animations
- optional AI metadata on saved animations
- Emotion Reactions mapping from saved animations
- fallback logic back to default hardcoded emotions

## Open On A New Machine

```powershell
git clone <repo>
git fetch origin
git switch experimental-animation-creator
```

Then open the Unity project normally.

## Important Files

- `Assets/ReachyControlApp/Scripts/ReachyRuntimeControlUI.cs`
- `Assets/ReachyControlApp/LocalVoiceAgent/local_voice_agent_sidecar.py`

Generated or machine-local files should usually not be treated as the source of truth for this experiment:

- `Assets/ReachyControlApp/voice_agent_config.json`
- `Assets/ReachyControlApp/LocalVoiceAgent/local_voice_agent_sidecar_config.json`
- `Assets/ReachyControlApp/LocalVoiceAgent/local_voice_agent_sidecar_last_run.log`

## Animation JSON Location

Animation Creator saves local JSON animations under Unity's persistent data path in the `ReachyAnimations` folder.

On Windows this is typically:

```text
C:\Users\<YourUser>\AppData\LocalLow\Pollen Robotics\Reachy controller _ simulator\ReachyAnimations
```

Example test file used during development:

```text
agree-test.json
```

These JSON files are not automatically part of the repo unless you explicitly add sample files somewhere tracked.

## Current Experimental Workflow

1. Create or import an animation in Animation Creator.
2. Fill in:
   - `Pose title`
   - `Description`
   - `Suggested emotion key`
   - `Suggested AI use`
   - `Use this animation in AI Mode`
3. Press `Save locally`.
4. Select the saved animation.
5. Press `Create / Update Emotion Reaction`.

## Current Caveats

- This is a work in progress and may be clunky.
- Unity play mode testing is still required after pulling the branch on a new machine.
- If `Use this animation in AI Mode` is disabled, Emotion Reactions should fall back to default hardcoded motions when a built-in fallback exists.
- Custom saved animations and local config state may differ across machines unless the required JSON files are recreated or shared.

## Recommended Branch Maintenance

- Keep implementation changes in this branch.
- Avoid committing machine-specific config/log churn unless it is intentionally part of the experiment.
- If `main` changes later, merge or rebase `main` into this branch when needed.
