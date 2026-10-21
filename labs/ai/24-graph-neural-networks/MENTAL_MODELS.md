# Mental Models: Graph Neural Networks

## 1. Optimization Landscape
Think of loss as a landscape. Gradient descent is like walking downhill in fog - you can feel the slope at your feet but can't see the whole terrain.

## 2. Function Approximation
The model is like a curve-drawing machine. Simple models draw smooth curves; complex models can follow every data point but may capture noise.

## 3. Feature Learning
Layers build increasingly abstract concepts. Early layers detect edges; middle layers detect shapes; deep layers detect objects. Like how human vision processes information.

## 4. Information Compression
The model must compress input information while preserving what's relevant for the task. This forces it to learn the essential structure.

## 5. Neural Darwinism
Random initialization creates variation. Loss function selects for useful parameters. Training iterations propagate beneficial changes.

## 6. Bayesian Update
Initial beliefs (prior) are updated with evidence (data) to form new beliefs (posterior). More data narrows uncertainty.
