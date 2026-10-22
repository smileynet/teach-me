# Resources

Verified sources for the world-models workspace. Primary = two explored projects (L1, the code;
non-public, described generically); secondary = public prior art (L2-L6).

## Primary sources — two projects (L1:verified, non-public)

| Project | What it demonstrates |
|------|----------------------|
| FDS benchmark (a world-model evaluation project) | The FDS evaluation benchmark: engine-as-oracle, the four-axis harness, a two-phase benchmark proposal |
| Real-time PoC (a world-model proof of concept on Trainium) | A real-time RF/Wan2.1 world model on Trainium: causal DiT, Rolling Forcing, DMD distillation, action conditioning, the ~14 fps baseline |

### Verified facts (source-verification pass, 2026-09-17)

- Behavioral FDS = `1 - action_F1` — macro-F1 over discrete action
  channels via IDM round-trip. **Not** a Fréchet distance, **not** FVD. `camera_l1` is
  reported but **not** folded into the trusted scalar.
- RF = Wan2.1-T2V-1.3B (~4 fps interactive); MG3 = Wan2.2-5B (~17 fps, 4×H100). The **~14 fps** =
  RF offline on **Trainium2**, TP4×CP4=16, 480×640, 5 denoise steps.
  Trn2-vs-GPU parity is **not** stated in the source — do not claim it.

## Prior-art research (tagged [L#:confidence])

| Topic area | Source (representative) | Trust |
|------------|-------------------------|-------|
| World-model eval prior art | FVD (arXiv:1812.01717), CD-FVD (CVPR 2024), VBench/WorldModelBench; IDM-round-trip lineage VPT→Genie→RLIR (arXiv:2509.23958) | L2-L4 |
| Real-time WM serving | Decart (Oasis/Mirage); Self-Forcing + WebRTC + step-distillation reference stack | L4-L5 |
| Neuron/Trainium inference | NxD Inference (NeuronX Distributed Inference) docs; NKI programming guide; Activation Memory Reduction (TP/SP) guide | L4:verified |
| Real-time serving on AWS | SageMaker real-time endpoints + `InvokeEndpointWithResponseStream` (HTTP chunked streaming) | L4:verified |

## AWS-doc anchors for the serving topic (the SageMaker-Async analog)

Two docs thread through the serving/accelerators topic (mirroring how Async anchors the sibling
domain):

| Anchor | URL | Anchors what |
|--------|-----|--------------|
| NxD Inference (NeuronX Distributed) | https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/index.html | Accelerator-native serving on Trainium; TP/SP/CP config |
| NKI programming guide | https://awsdocs-neuron.readthedocs-hosted.com/en/latest/general/nki/ | The kernel lever (the PoC's NKI kernels) |
| SageMaker real-time + response streaming | https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html + `InvokeEndpointWithResponseStream` | Interactive/streaming delivery of generated frames |

**Honest gap (carry into the lesson):** there is **no first-party AWS doc for real-time *video
generation* on accelerators** — only image-DiT (PixArt-Σ/SDXL) and video *understanding* blogs. A
"real-time video generation on Trainium" claim is extrapolation from DiT image serving + streaming
delivery, not a documented AWS workflow. Neuron doc URLs use `/en/latest/` and churn per release —
pin to a specific version at authoring time.

## Source-authority note

Running code (L1) wins for "what these projects do"; the AWS doc (L4) wins for "what the managed
service/accelerator supports." Decart claims are L4-L5 (awareness/reported), not first-party
contracts.
