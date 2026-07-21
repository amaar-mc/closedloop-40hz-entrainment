# Computational Deep Dive

For if a CS/ML specialist judge visits your Medicine & Physiology booth. Less likely than medical questions, but possible. Keep these in your back pocket.

---

**Q1. "Why causal convolutions specifically?"**
In a real-time system, you don't have future data. Causal convolutions enforce this at the architecture level -- left-only padding means computation at time T depends only on T and earlier. With an RNN, causality depends on correct implementation of hidden state propagation. With a Transformer, you need explicit causal masking. The TCN makes it structural. You literally cannot leak future information even if you try.

**Q2. "Explain dilated convolutions and the receptive field."**
Standard convolutions look at adjacent time steps. Dilated convolutions skip steps -- dilation of 2 looks at every other step, dilation of 4 every fourth. My TCN stacks dilations [1, 2, 4, 8], so each layer doubles the receptive field exponentially while keeping parameter count linear. With kernel size 3 and 4 layers, the effective receptive field is 1 + sum(2 _ (3-1) _ d for d in [1,2,4,8]) = 31 steps. That covers 31 seconds of history from 20 input steps.

**Q3. "Why not attention? Your sequence is only length 20."**
Three issues. First, self-attention is O(n^2) in sequence length and while n=20 is small, the data budget is the real problem -- 17,000 windows with length-20 sequences isn't enough to train attention weights without overfitting. Second, attention doesn't guarantee causality without explicit masking. Third, my TCN with depthwise separable convolutions has 22,914 params. A minimal Transformer with comparable capacity would have more parameters and need more data. I tested Transformer variants -- the TCN won.

**Q4. "Why GroupNorm instead of BatchNorm?"**
BatchNorm statistics are computed per batch and depend on which subjects happen to be in each batch. Subject-to-subject PAC variation is large, so batch statistics shift unpredictably. GroupNorm normalizes within channel groups of each sample independently, making it stable across subjects. This is the same reason InstanceNorm works better in style transfer -- per-sample normalization handles domain shift.

**Q5. "How did you prevent overfitting with 17K windows?"**
Multiple layers: subject-level splits (no within-subject leakage), dropout, weight decay via AdamW, early stopping with patience 20, gradient clipping at max_norm 1.0, and the feature reduction itself -- going from 73 to 12 features was the biggest regularizer. The val-test gap shrank from 0.358 to 0.246 after the feature drop. Also, the TCN is deliberately small: 22,914 parameters. Not enough capacity to memorize the training set.

**Q6. "Explain the dual-head output."**
The TCN produces two outputs: future PAC value and delta-PAC (change from current to future). Multi-task training with Huber loss on both heads plus a consistency penalty. The delta head helps the model focus on the direction and magnitude of change, not just the absolute value. The consistency penalty ensures the two heads agree: predicted future PAC should approximately equal current PAC plus predicted delta. During inference, the controller uses the future PAC head.

**Q7. "What's the actual inference latency breakdown?"**
Feature extraction: ~5 ms (rolling window statistics, all NumPy). TCN forward pass: ~2 ms on CPU. Controller decision: ~1 ms (z-score computation, threshold comparison). Total: under 10 ms on a laptop CPU. The 50 ms figure I report is conservative with overhead. Real-time EEG sampling at 250 Hz gives a new sample every 4 ms, and we only need a prediction every 1-2 seconds. Inference is not the bottleneck.

**Q8. "Could this run on edge hardware? Raspberry Pi? Mobile phone?"**
The TCN is 22K parameters. That's tiny. It would run on a Raspberry Pi, a phone, or even a microcontroller. The bottleneck isn't the model -- it's the EEG acquisition. Consumer headsets like Muse 2 stream over Bluetooth, which adds latency. On-device inference with a dedicated EEG front-end would work. I haven't tested deployment on edge hardware, but the model size isn't a constraint.

**Q9. "Why depthwise separable convolutions?"**
Factorizes the convolution into depthwise (per-channel) and pointwise (cross-channel) operations. Reduces parameters from (K _ C_in _ C_out) to (K _ C_in + C_in _ C_out). With K=3 and C=64, that's roughly 3x fewer parameters per layer. Important when data is limited -- every unnecessary parameter is a potential overfitting vector.

**Q10. "Walk me through a single forward pass."**
Input: (batch, 20, 12) -- 20 timesteps, 12 features. First, input projection from 12 to hidden_dim (64) via 1x1 conv. Then 4 causal depthwise-separable conv blocks at dilations 1, 2, 4, 8, each with GroupNorm and SiLU activation, plus residual connections. Output sequence: (batch, 20, 64). Attention pooling aggregates across time to (batch, 64). Then two separate FC heads: one predicting future PAC (batch, 1), one predicting delta-PAC (batch, 1). During training, both heads contribute to the loss. During inference, we take the future PAC prediction.
