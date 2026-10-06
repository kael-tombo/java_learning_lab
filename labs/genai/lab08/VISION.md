# Lab 08: Multimodal Models — Vision

## Two Architectures Side by Side

```
DUAL ENCODOR (CLIP)                      CROSS-ATTENTION VLM
  image [224x224]                          image -> vision tower
      |                                        |
  vision encoder                          M visual tokens (e.g. 576)
      |                                        |
   z_i (D=768)                          + PROJECTOR / resampler
      |                                        |
      |        text -> tokenizer               |  K tokens (e.g. 64)
      |              |                          |
      |        text encoder                     v
      |              |                   [visual ; text]  <- ONE sequence
      |        t_i (D=768)                     |
      |              |                     causal mask on TEXT only
      +--> s_ij = z_i . t_j / tau                |
              |                             LLM decoder
              v                                 |
        similarity / retrieval                    v
                                          generated text

  cost: O(N) once per item, no generation    cost: O((M+L)^2) attention per query
  use: retrieval, dedup, ranking            use: answering, reasoning, OCR
```

## Sequence Construction — Where the Mask Goes

```
keys/values:   [ v_1  v_2  ...  v_M ][ t_1  t_2  t_3 ]
index:           0    1         M-1     M    M+1   M+2

query t_1 (abs pos M)     attends [v_1 .. v_M, t_1]              -> M+1 keys
query t_2 (abs pos M+1)   attends [v_1 .. v_M, t_1, t_2]          -> M+2 keys
query t_3 (abs pos M+2)   attends [v_1 .. v_M, t_1, t_2, t_3]      -> M+3 keys

  X X X X X X X X X X  X  X  X        X = allowed
  X X X X X X X X X X  X  X  X  X     . = blocked (future text)
  X X X X X X X X X X  X  X  X
  |<--- visual: always visible --->|
                                 |<--- text: causal --->|

  OFF-BY-ONE HAZARD:
  bound must be mVisual + qi + 1, not mVisual + qi
  too small -> drops the CURRENT token (silent quality loss)
  too large -> leaks the FUTURE (silent correctness loss)
```

## Resolution vs Token Count

```
token count = (H/P) * (W/P)

  image     P     tokens   vs 224   attention cost   vision tokens vs LLM tokens
  224x224   16       196        1.0x                   full detail
  336x336   14       576        8.6x                   3x more
  448x448   14      1024       27x                    5x more
  896x896   14      4096      436x                    21x more  (impractical)

  naive single-image: 1024 visual tokens + 64 text = 1088  (17x text-only cost)
  tiled 4x512 crops,  K=64 each resampled:  64 + 64  = 128  (2x text-only cost)
                                                               <-- projector wins
```

## Contrastive Training Geometry

```
batch of N=8 pairs, tau=0.05

                t_1     t_2     t_3     t_4     t_5     t_6     t_7     t_8
  z_1          .28     .02    -.05     .01     .00    -.03     .04     .03
  z_2          .01     .31     .00    -.02     .02     .05    -.01     .00
  z_3         -.03     .01     .29     .03    -.01     .00     .02    -.02
  ...
        ^ diagonal = matched pairs; off-diagonal = FREE negatives

  loss_i = -log( exp(s_ii) / sum_j exp(s_ij) )
  diagonal 0.29 -> exp=1.34 ; off-diag 0.04 -> exp=1.04
  loss_i = -log(1.34 / (1.34 + 7*1.05)) = -log(0.155) = 1.86

  if all s_ij ~ 0 -> loss = ln 8 = 2.08      (random)
  if diagonal 5.0, off 0    -> loss = -log(1/(1+7e-5)) = 0.0007   (learned)

  gradient on pair i ~ (p_ii - 1)/tau : ZERO when already correct
  -> tau must be small enough that near-misses still get gradient
```

## Temperature Effects

```
tau too large (1.0)                tau too small (0.001)
  logits ~ z.t in [-1,1]            logits ~ z.t/0.001 = [-1000,1000]
  p_ii ~ 1/N for everything        p_ii saturates to 1 instantly
  gradient ~ 1e-3 (tiny)            gradient ~ (p_ii-1)*1000 -> oscillation,
  performance ~ random                  possible overflow in fp16

tau optimal (0.02-0.07)
  off-diagonal gap ~ 1/tau = 14-50 logits
  p_ii rises fast but not instantly
  stable, informative gradients
```

## Fusion Strategies Compared

```
EARLY FUSION               LATE FUSION              CROSS-ATTENTION
  [img_feat ; txt_feat]      img -> v1               visual ─┐
       |                    txt -> t2               text  ──┼> cross attention
  single encoder                 |                          v
  cheap                          +--> score fusion       one joint representation
  needs aligned data        cheapest                     most expressive
  no generation              no generation              generation + reasoning
                             (retrieval, ensembles)    (VQA, agents, OCR)

PROJECTOR (the modern bridge)
  vision tower (frozen)  ->  visual tokens  ->  [resampler]  ->  K tokens
                                                                  |
                                                            LLM embedding space
  K tokens is a HARD BUDGET: attention cost independent of image resolution
```

## Training Stages

```
STAGE 1: VISION PRETRAINING
  images + captions (or pure images)
      |
      +--> CLIP contrastive       -> general visual features, aligned to text
      +--> MAE / DINO             -> dense features, no text needed
      v
  frozen or LoRA'd vision tower

STAGE 2: PROJECTOR ALIGNMENT
  freeze vision tower AND LLM
  train ONLY the projector/resampler
  objective: next-token prediction of the caption
  v
  visual tokens now live in the LLM's embedding space

STAGE 3: INSTRUCTION TUNING
  vision tower frozen (sometimes unfrozen late in training)
  train projector + LLM (LoRA on LLM)
  data: VQA, OCR-heavy, grounding (bbox), multi-turn conversation, charts, tables
  v
  instruction-following VLM

STAGE 4: PREFERENCE OPTIMIZATION (Lab 07)
  DPO on preference pairs over model answers
  include helpfulness AND visual faithfulness
  v
  aligned VLM
```

## Multimodal RAG Architecture

```
  query (text)
      |
      v
  text encoder -> qv (normalized)
      |
      v
  CLIP image index  (1 embedding per image, Lab 04 infra)
      |            cosine top-k
      v
  top-3 images + scores
      |
      v
  VLM prompt:  [img_1] [img_2] [img_3]  +  query
      |
      v
  answer with [i] citations
      |
      v
  CitationChecker: every [i] must resolve to a retrieved image id
      |
      v
  FaithfulnessCheck: every noun in the answer appears in some retrieved caption
      |
      v
  response + source thumbnails + confidence

  WHY TWO STAGES: retrieval must be cheap per ITEM (millions);
                  answering must be precise per QUERY (thousands)
```

## Failure Modes

```
ground-truth: 3 circles + 1 square
model:        "There are three squares and a circle."

                 +-- language prior wins over weak visual evidence
                 |   (the training caption distribution dominates)
                 |
input image --> [ vision tower ] --(weak signal)--> [ projector ] --> [ LLM ]
                                              |            |
                                              v            v
                                     patch grid too coarse  sees "3 objects",
                                                            completes "squares"

symptom -> fix
  wrong object names   -> faithfulness training, more grounding data
  small text unreadable-> higher resolution, tiling, OCR-aware pretraining
  counting errors      -> counting data in stage 3
  spatial errors       -> bbox supervision (IoU metric)
  biased captions      -> balanced data, attribute-sweep audit
  over-refusal         -> recalibrate per category
  image-borne injection-> treat image text as DATA (never instructions)
```

## Self-Check

- [ ] Visual tokens fully visible; causal mask on text only.
- [ ] Bound is `mVisual + qi + 1`.
- [ ] Projector caps visual tokens at a fixed K.
- [ ] Same contrastive model for query and index.
- [ ] Citations verified against retrieved ids, not just ranges.
- [ ] Image text treated as untrusted input.