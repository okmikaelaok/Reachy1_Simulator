
# Reachy 1 Controller and Simulator

**Upstream:** [Sami Kamara's project](https://github.com/SamiKamara/reachy1-unityproject) was used to extend these features.

This project was developed as part of the HTI.460 course, Social Robots: Design, Research and Interaction (March–May 2026). Reachy 1 was the primary robot used, serving as a platform to support and enhance participants’ robot and AI literacy. The selected dimension within this literacy framework was “envisioning robots in the future”, a recently introduced dimension developed by the course instructors, building on prior work by Ahtinen et al. (2025) in Robotour for Seniors – A Co-Learning Model to Enhance Robot Literacy among Older Adults in the Care Home Context (International Journal of Social Robotics, 17, 1201–1220). https://doi.org/10.1007/s12369-025-01277-8.

| Symbol | Meaning |
|--------|---------|
| 🟢 | Indicates features tested on the physical robot and accurately reflected in the simulation |
| 🟡 | Indicates features not yet tested; real-world behavior may differ |


-----

### Features Added & Focused On:
`Animation Creator tab` 09.04.2026 🟢

This allows you to create, save and delete animated poses for Reachy. Useful for creating new animation sequences like reactions and emotions.

- `Joint sliders`: Move any of Reachy's joints with sliders.
- `Animate Reachy's avatar with mouse` (WiP): Use Reachy’s 3D avatar to animate joints by clicking and dragging them directly.
- `Keyframe recording`: Create animation sequences by setting joint positions and saving them frame by frame.
- `Save animation sequence`: Save created animations and delete them during runtime as needed.

`Chit Chat tab` 14.04.2026 🟢

This allows you to have conversations with Reachy using text. Responses are sent via TTS. Useful in noisy environments and if STT fails.

- `Text chat`: Ask any questions to Reachy using mic or text and see your conversations.
- `Mic/Text Transcripts`: Log mic or text input into the chat bubbles, with the option to clear the chat or save it locally.
- `Topic buttons`: These are pre-defined topic buttons that will prompt Reachy to generate relevant dialogue e.g. tell me more about the future of robots in education.
- `Syncs with AI personas`: A chosen persona from AI Mode will still work e.g. coffee mug.
- `Interrupt Reachy`: With the Stop button, Reachy's movements and speech can be interrupted at any time.

`some features in AI Mode tab `

Added the following...
- Scrollwheel for the `Base prompt text box`.
- Multi-select delete checkboxes in `Browse saved personalities` to prevent duplicates.

### Videos

https://github.com/user-attachments/assets/aaa93e5c-b712-461a-8bcd-d636543b219e

https://github.com/user-attachments/assets/8ec6aaba-ab25-4255-b3bf-376ff6cbb74e

### Notes & Possible Future Iterations

* The UX and UI can be improved. Utility and core functionality were prioritized first.

* `Animation Creator tab` can be improved by adding:

  * permanent local saving of animation sequences (JSON-based) instead of runtime-only storage, reducing hardcoded logic
  * import/export functionality to improve sharing and management of animations
  * sync and mapping with AI Mode so created animations can be directly linked to behaviors, emotions, or triggers
  * a 3D rotation XYZ control (gizmo/ball) to allow easier camera manipulation instead of a static front-facing view
  * highlighting of selected joints to improve usability, with synchronization between the 3D avatar and corresponding UI buttons
  * mirror left/right functionality so paired joints (e.g. shoulders, arms) move symmetrically, improving consistency in body movements
  * support for attaching audio to specific animations for more expressive behavior
  * an option to save animations to a General (or Quick Actions) section for quick access


* `Chit Chat tab` can be improved by adding:

  * ✅ a transcript log that distinguishes between mic and text input (useful for verifying what input was successfully processed)
  * ✅ local saving of transcripts
  * ✅ ability to clear chats 
  * pinning of specific chat bubbles for persistent memory and easy reference

* `AI Mode tab` can be improved by adding:

  * sync and mapping with the Animation Creator tab
  * Dance mode (to trigger predefined animation sequences such as Macarena, Crab Rave, SpongeBob Electric Zoo)
  * Tone control (e.g. optimistic, dystopian, realistic) to adjust response style and behavior
  * Max response control (in characters/tokens) to manage response length


