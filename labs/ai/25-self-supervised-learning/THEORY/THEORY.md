# Self-Supervised Learning — Theory

**Self-supervised learning** trains a representation without human-provided labels:
signals are manufactured from the data itself. The leading recipe is *contrastive*: create
two variants of the same object ("views"), keep views of the same object close in
embedding space, and push views of different objects apart.

## The contrastive setup

- An augmentation policy generates views (color jitter and crops for images; masking and
  shuffling for text; time-warping for signals). The view pair is a *positive*.
- Everything else in the batch acts as a *negative* (in the one-sided variant), which is
  why batch composition matters more than in supervised learning.
- The encoder maps views to vectors; a small projection head usually maps further before
  the loss is applied (SimCLR-style practice) — the head is thrown away afterward, and the
  frozen encoder is transferred to downstream tasks.

## Loss shape

The standard objective is InfoNCE — a softmax over cosine similarities between the anchor
and the candidate set, compared at a temperature `tau`. At small `tau` the near-identical
positive dominates and the loss approaches 0; at large `tau` all candidates pull their
weight and the loss approaches a uniform baseline. The temperature is thus a soft
"selector sharpness" knob, and the snippet in this folder makes that behavior numeric.

## Other families (brief, concept-level only)

- Predictive: predict one view from the other (or from a context), turning the signal into
  a masked-prediction task rather than a ranking task.
- Clustering-based: group embeddings, then treat cluster-membership agreement between two
  views as the label; avoids explicit negatives but introduces its own instability tricks.
- Bootstrap-style pairs: two encoders, one updated more slowly than the other, keeping
  targets stable without negatives at all.

## What gets evaluated

Linear-probe style transfer: freeze the encoder, train a linear classifier on a small
labelled set, and report its accuracy against a from-scratch baseline. Image retrieval and
nearest-neighbor transfer are also common. Any accuracy number you read is tied to a
specific dataset and augmentation stack; generalizing across them is not automatic — the
exercises here only build the loss machinery, never a benchmark claim.

## Connection to the rest of the lab

The same seeded-RNG discipline and fixed-vector arithmetic used elsewhere applies here:
InfoNCE reduces to exp/log arithmetic over a handful of stored vectors, so Java can
reproduce every intermediate value by hand.
