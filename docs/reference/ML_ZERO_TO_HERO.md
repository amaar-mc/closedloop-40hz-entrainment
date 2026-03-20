# Machine Learning: Zero to Hero
## From "What's a Neural Network?" to "Why I Built a Causal TCN for Brain Entrainment"

> Read this top to bottom. Every term is introduced before it's used.
> By the end, you'll understand every model decision in this project.

---

## PART 1: FOUNDATIONS

### 1.1 What Is Machine Learning?

Traditional programming: you write rules, the computer follows them.

```
IF temperature > 100:
    alarm = ON
```

Machine learning: you give the computer examples, and it **learns the rules itself**.

```
Given 10,000 examples of (temperature, humidity, pressure) -> (alarm ON or OFF)
The computer figures out: "alarm should be ON when temperature > 97 AND humidity > 60"
```

You never wrote that rule. The computer discovered it from patterns in data.

**Why this matters for our project:** We can't write a rule like "stimulate when
the EEG looks like X" because brain signals are incredibly noisy and vary between
patients. Instead, we give the model thousands of examples of EEG windows paired
with PAC values, and it learns the relationship.


### 1.2 What Is a Neuron (in ML)?

A biological neuron receives signals, processes them, and fires (or doesn't).
An artificial neuron does the same thing mathematically:

```
INPUTS           WEIGHTS          SUM + BIAS       ACTIVATION       OUTPUT
                                                   FUNCTION
x1 ---(*w1)---\
                \
x2 ---(*w2)----->  (x1*w1 + x2*w2 + x3*w3 + b)  -->  f(sum)  -->  output
                /
x3 ---(*w3)---/
```

Step by step:
1. **Inputs** (x1, x2, x3): Numbers coming in. Could be pixel values, EEG voltages, anything.
2. **Weights** (w1, w2, w3): How important each input is. These are the numbers the model LEARNS.
3. **Bias** (b): A constant offset. Also learned.
4. **Sum**: Multiply each input by its weight, add them all up, add the bias.
5. **Activation function** f(): A mathematical function applied to the sum. This is what
   makes neural networks capable of learning complex patterns (more on this below).
6. **Output**: A single number that gets passed to the next neuron.

**Key idea:** A single neuron is just a weighted sum followed by a function. It's
basically a fancy version of y = mx + b (a line). By itself, not very powerful.


### 1.3 Activation Functions: Why We Need Them

Without an activation function, a neuron computes: output = w1*x1 + w2*x2 + b.
That's a straight line. Stack 100 of these together and you still get... a straight line.
Linear combinations of linear functions are linear. You can't model curves.

Activation functions add **non-linearity** -- the ability to model curves, thresholds,
and complex patterns.

Common activation functions:

```
ReLU (Rectified Linear Unit):        ELU:                    SiLU (Sigmoid Linear Unit):
                                                    
output                               output                  output
  |      /                             |      /                |       __/
  |     /                              |     /                 |     /
  |    /                               |    /                  |    /
  |   /                                |   /                   |   |
  |__/                              \__|  /                    |__/
  +----------input                  ---+----------input        +----------input
  0                                    0                       0
                                                    
  If input > 0: output = input      Like ReLU but slightly   Smooth curve. x * sigmoid(x).
  If input < 0: output = 0          negative for input < 0.  No dead neurons. No hard cutoff.
  Simple. Fast. But "dead neurons"  Used in EEGNet.          Used in our TCN.
  -- once a neuron outputs 0, it
  may never recover.
```

**In this project:**
- EEGNet uses **ELU** (smooth, slightly negative for negative inputs)
- The Causal TCN uses **SiLU** (smooth, no dead neurons, better gradient flow)


### 1.4 What Is a Neural Network?

A neural network is just **layers of neurons connected together**.

```
INPUT LAYER          HIDDEN LAYER 1        HIDDEN LAYER 2        OUTPUT LAYER
(your data)          (learned features)    (higher features)     (prediction)

  x1 ----\__________  h1 ----\__________   h4 ----\__________    
          \________/  h2 ----/\________/   h5 ----/\________/   output
  x2 ----/\________\  h3 ----\           / h6 ----/              
          /________/                    /                       
  x3 ----/                                                      
```

- **Input layer:** Your raw data (e.g., EEG voltages from 7 channels)
- **Hidden layers:** Intermediate processing. Each neuron learns some feature.
  "Hidden" just means you don't directly see what they compute.
- **Output layer:** The final prediction (e.g., a PAC value)

Every arrow is a weight. A network with 3 inputs, 3 hidden neurons, and 1 output
has 3*3 + 3*1 = 12 weights plus biases. That's what the model "learns."

**More layers = ability to learn more complex patterns.** But also more risk
of memorizing noise instead of learning real patterns (overfitting -- covered below).


### 1.5 What Is a "Parameter"?

A **parameter** is any number the model learns during training. This includes:
- All weights (the multipliers on connections between neurons)
- All biases (the constant offsets)

When we say "EEGNet has 1,457 parameters," we mean there are 1,457 numbers that
the training process adjusts to make the model's predictions match reality.

When we say "the Causal TCN has 31,043 parameters," that's 31,043 adjustable numbers.

**More parameters = more capacity to learn complex patterns, but also more risk
of overfitting when you don't have enough training data.**


### 1.6 How Does a Network Learn? (Training)

Training has four steps, repeated thousands of times:

#### Step 1: Forward Pass
Feed an input through the network. Get a prediction.
```
Input: EEG window from patient 7
Prediction: PAC = 0.00032
Actual PAC: 0.00058
```

#### Step 2: Compute Loss
The **loss function** measures how wrong the prediction was.

```
MSE (Mean Squared Error):     Loss = (prediction - actual)^2
                              Loss = (0.00032 - 0.00058)^2
                              Loss = 0.00000000068

Huber Loss:                   For small errors: same as MSE
                              For large errors: linear (not squared)
                              Why? Outliers don't dominate. (Used in our TCN)
```

The loss is a single number. Lower = better. The goal of training is to
**minimize the loss across all training examples.**

#### Step 3: Backward Pass (Backpropagation)
This is the clever part. The network asks: "For each of my 31,043 parameters,
if I nudge it slightly up or slightly down, does the loss get better or worse?"

This is computed using calculus (the chain rule of derivatives). The result is
a **gradient** for each parameter -- a direction that says "adjust this parameter
THIS way to reduce the loss."

You don't need to understand the calculus. Just know that backpropagation
efficiently computes which direction to adjust every parameter.

#### Step 4: Update Parameters
Each parameter is nudged in the direction that reduces the loss:

```
new_weight = old_weight - learning_rate * gradient
```

The **learning rate** controls how big the nudge is:
- Too large: overshoots, bounces around, never converges
- Too small: learns extremely slowly
- Our project uses lr = 0.001 (a standard safe default)

**One complete cycle of steps 1-4 across ALL training examples = one EPOCH.**
Our TCN trains for about 53 epochs before stopping.


### 1.7 What Is an Optimizer?

The optimizer is the specific algorithm that decides HOW to update parameters.
Simple gradient descent does: `weight -= lr * gradient`. But smarter optimizers
exist:

**Adam** (used in EEGNet training):
- Keeps a running average of past gradients (momentum)
- Adapts the learning rate separately for each parameter
- Parameters that rarely get large gradients get bigger updates
- Standard choice, works well in most cases

**AdamW** (used in TCN training):
- Same as Adam but handles weight decay (regularization) more correctly
- "W" stands for "decoupled Weight decay"
- Better at preventing overfitting in practice


### 1.8 Overfitting vs. Underfitting

This is one of the most important concepts in ML.

```
UNDERFITTING                    GOOD FIT                      OVERFITTING
(too simple)                    (just right)                  (too complex)

  *       *                      *       *                     *       *
      *       *                    *   *   *                  * * *   * * *
  *       *                    *           *                *   *   *   *
      *       *                  *       *                    *       *
  ____________                 ____~~~~____                 __/\__/\__/\__
  straight line                smooth curve                wiggly mess

  Model is too simple          Model captures the           Model memorized
  to capture the               real underlying              every data point
  real pattern.                pattern.                     including NOISE.
  Bad on training data.        Good on ALL data.            Great on training,
  Bad on new data.             Good on new data.            TERRIBLE on new data.
```

**Overfitting is the central enemy of this project.** We have only ~11,000
training samples. Models with too many parameters memorize the training data
perfectly but fail on new patients. That's why:

- EEGNet has only 1,457 params (not 100,000)
- The TCN has only 31,043 params (not 1,000,000)
- We use regularization techniques (next section)


### 1.9 Fighting Overfitting: Regularization Techniques

Several tools exist to prevent a model from memorizing noise:

**Dropout:**
During training, randomly set some neurons to zero (turn them off).
```
Normal:    [h1=0.5] [h2=0.3] [h3=0.8] [h4=0.1]  --> all contribute
Dropout:   [h1=0.5] [  0.0 ] [h3=0.8] [  0.0 ]  --> h2, h4 turned off
```
Forces the network to be redundant -- it can't rely on any single neuron.
Next training step, different neurons are dropped. The network learns
robust features that work even when some neurons are missing.

- EEGNet uses Dropout(0.5) -- 50% of neurons dropped. Very aggressive.
- TCN uses Dropout(0.1) -- 10% dropped. Lighter touch (has other regularization).

**Weight Decay (L2 Regularization):**
Add a penalty to the loss for having large weights:
```
total_loss = prediction_loss + weight_decay * sum(all_weights^2)
```
This discourages the model from assigning huge importance to any single feature.
Keeps weights small and predictions smooth.

**Early Stopping:**
Monitor performance on a VALIDATION set (data the model never trains on).
When validation performance stops improving, STOP training -- even if training
performance is still getting better. The gap between training and validation
performance = overfitting.

```
                Training loss keeps falling
Performance     \_________________________
  ^              \
  |    Validation  \________
  |    loss stops          \________   <-- STOP HERE (patience exceeded)
  |    improving                    \___________
  +-------------------------------------------------> Epochs
       |<-- good -->|<--- overfitting zone --->|
```

Our TCN uses patience=20: if validation R2 doesn't improve for 20 consecutive
epochs, training stops. Best epoch was 53.

**Gradient Clipping:**
Cap the magnitude of gradients during backpropagation. If a gradient is
larger than max_norm (1.0 in our case), scale it down. Prevents one
outlier sample from causing an explosive parameter update.


### 1.10 Train / Validation / Test Splits

You NEVER evaluate a model on the same data it trained on. That would be
like giving students the answer key before the exam and then claiming
they're geniuses.

```
ALL DATA (35 patients, 17,283 windows)
|
|-- TRAIN (24 patients, 67.9%) -- Model learns from this
|
|-- VALIDATION (5 patients, 15.8%) -- Used during training to detect overfitting
|                                     Model never trains on this, but we peek
|                                     at it to decide when to stop training
|
|-- TEST (6 patients, 16.3%) -- LOCKED AWAY until the very end
                                Model has NEVER seen this data
                                Final reported results come from here
```

**CRITICAL: We split by PATIENT, not by window.** If patient 7 has windows
in both training and test, the model could memorize patient 7's brain patterns
during training and "cheat" during testing. Every window from a given patient
is in exactly one split. This is called **subject-level splitting** and is
non-negotiable in medical ML.


### 1.11 What Is R-squared?

R-squared (R2) is how we measure prediction quality. It answers:
"How much of the variation in the data does my model explain?"

```
R2 = 1 - (sum of squared prediction errors) / (sum of squared deviations from mean)
```

Interpretation:
- R2 = 1.0: Perfect. Every prediction exactly matches reality.
- R2 = 0.5: Model explains 50% of the variance. Decent.
- R2 = 0.0: Model is no better than just predicting the average every time.
- R2 < 0.0 (negative): Model is WORSE than predicting the average.
              Its predictions are actively misleading.

**In this project:**
- EEGNet static PAC estimation: R2 = 0.287 (explains 28.7% of variance)
- TCN at 5-second horizon: R2 = 0.254 (modest, but positive where all baselines are negative)
- Persistence baseline at 5s: R2 = -0.267 (worse than predicting the mean)


### 1.12 Normalization: Why and How

Brain signals vary wildly between patients. Patient A might have PAC values
around 0.0001, while patient B is around 0.0008. If we feed raw values to
the model, it gets confused by the scale differences.

**Z-score normalization:**
```
normalized_value = (value - mean) / standard_deviation
```

This transforms all values to have mean=0 and std=1. Now both patients'
data lives in the same range, roughly -3 to +3.

**CRITICAL RULE:** Compute mean and std from TRAINING data only. Then apply
those same numbers to validation and test data. If you compute statistics
on test data, you're "peeking at the future" -- the model implicitly knows
something about test patients it shouldn't.

Our project stores these statistics in `scalers.npz` and loads them during
inference, ensuring no leakage.


---

## PART 2: CONVOLUTIONS

### 2.1 What Is a Convolution?

Forget the math definition. A convolution is a **sliding window operation.**

Imagine you have a 1D signal (like one channel of EEG):

```
Signal:  [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
```

And a small **filter** (also called a **kernel**):

```
Filter:  [1, 0, -1]    (length 3)
```

The convolution slides the filter across the signal, computing a weighted
sum at each position:

```
Position 1:  3*1 + 1*0 + 4*(-1) = 3 - 4 = -1
Position 2:  1*1 + 4*0 + 1*(-1) = 1 - 1 =  0
Position 3:  4*1 + 1*0 + 5*(-1) = 4 - 5 = -1
Position 4:  1*1 + 5*0 + 9*(-1) = 1 - 9 = -8
Position 5:  5*1 + 9*0 + 2*(-1) = 5 - 2 =  3
...

Output:  [-1, 0, -1, -8, 3, ...]
```

**What did the filter [1, 0, -1] compute?** It subtracted the value two steps
ahead from the current value. It's a **change detector** -- the output is large
when the signal changes rapidly.

Different filters detect different things:
- [1, 1, 1] / 3 = smoothing (moving average)
- [1, 0, -1] = change detection
- [-1, 2, -1] = peak detection
- A 64-sample filter at 250 Hz = captures patterns spanning 256ms (one theta cycle)

**The key insight of CNNs:** Instead of hand-designing filters, we let the
network LEARN what filters are useful. The filter values become parameters
that are adjusted during training via backpropagation.


### 2.2 Convolution in 2D (Images and EEG)

For images, the filter slides in both directions (height and width):

```
Image patch:          Filter:           Output:
[1 2 3]              [1  0]            1*1 + 2*0 + 4*(-1) + 5*1 = 2
[4 5 6]              [-1 1]
```

For EEG, we have a 2D input too: (channels x time). A 2D convolution over
EEG can detect patterns across both channels and time simultaneously.


### 2.3 What Is a CNN (Convolutional Neural Network)?

A CNN stacks multiple convolutional layers:

```
INPUT          CONV LAYER 1        CONV LAYER 2         OUTPUT LAYER
               (low-level          (high-level
raw data        features)           features)            prediction

EEG signal --> [edge detector ] --> [pattern        ] --> [Linear] --> PAC
               [freq detector ]     [combiner       ]     
               [peak detector ]     [rhythm detector]     
               (8 learned          (16 learned           (weighted
                filters)             filters)              sum)
```

Layer 1 learns simple features (edges, frequencies, peaks).
Layer 2 combines those into complex features (rhythms, bursts, patterns).
The output layer combines all features into a prediction.

**Key properties of CNNs:**
- **Weight sharing:** The same filter is applied at every position in the signal.
  A peak detector works the same way whether the peak is at the start or end.
  This drastically reduces the number of parameters.
- **Local connectivity:** Each filter only looks at a small neighborhood.
  A 64-sample filter doesn't care about what happened 400 samples ago.
- **Translation invariance:** The network recognizes a pattern regardless
  of WHERE it occurs in the signal.


### 2.4 Pooling: Downsampling

After convolution, we often reduce the size of the output:

```
Before pooling:  [3, 1, 4, 1, 5, 9, 2, 6]   (8 values)

Average Pool (size 2):
  avg(3,1)=2  avg(4,1)=2.5  avg(5,9)=7  avg(2,6)=4

After pooling:   [2, 2.5, 7, 4]               (4 values -- half the size)
```

This does two things:
1. Reduces computation (fewer numbers to process)
2. Makes features more robust to small shifts in timing

EEGNet uses AvgPool to go from 500 timepoints down to 125, then down to 15.


### 2.5 Depthwise Separable Convolution (Important for EEGNet)

A standard convolution with C_in input channels, C_out output channels,
and kernel size K has: C_in * C_out * K parameters.

A **depthwise separable** convolution splits this into two steps:

```
STANDARD CONVOLUTION:                    DEPTHWISE SEPARABLE:

All inputs mixed with all outputs        Step 1 (Depthwise): Each channel filtered
at once.                                 INDEPENDENTLY. One filter per channel.
                                         Parameters: C_in * K
Parameters: C_in * C_out * K
                                         Step 2 (Pointwise): Mix channels using
                                         1x1 convolution.
                                         Parameters: C_in * C_out

                                         Total: C_in * K + C_in * C_out
```

Example with 16 input channels, 16 output channels, kernel size 3:
- Standard: 16 * 16 * 3 = 768 parameters
- Depthwise separable: 16 * 3 + 16 * 16 = 48 + 256 = 304 parameters

**2.5x fewer parameters for roughly the same expressive power.** When you have
limited training data (like our 11,000 samples), fewer parameters means less
overfitting. This is why both EEGNet and our TCN use depthwise separable convolutions.


### 2.6 EEGNet: A CNN Designed for Brain Signals

EEGNet (Lawhern et al., 2018) is specifically designed for EEG. It uses
convolution in a clever two-step process:

```
INPUT: (7 channels, 500 timepoints) = 2 seconds of EEG at 250 Hz

STEP 1 - TEMPORAL CONVOLUTION:
  8 filters of size (1, 64)        <-- 1 channel tall, 64 timepoints wide
  This slides ACROSS TIME within each channel independently.
  64 samples at 250 Hz = 256 ms = roughly one theta cycle.
  Each filter learns a different temporal pattern.
  Output: 8 feature maps, each (7 channels, 500 timepoints)

STEP 2 - SPATIAL CONVOLUTION (Depthwise):
  16 filters of size (7, 1)        <-- 7 channels tall, 1 timepoint wide
  This slides ACROSS CHANNELS at each timepoint.
  Kernel height = 7 = ALL channels. Learns which channels matter
  and how they relate to each other.
  Output: 16 feature maps, each (1 channel, 500 timepoints)

STEP 3 - SEPARABLE CONVOLUTION:
  Refines features with depthwise + pointwise convolution.

STEP 4 - FLATTEN + LINEAR:
  Collapse all features into a single number: the PAC estimate.

Total: 1,457 parameters. Tiny. That's the whole model.
```

**Why EEGNet is elegant:**
- Temporal conv captures frequency patterns (each filter learns a different rhythm)
- Spatial conv captures channel relationships (which brain regions matter)
- Separable conv reduces parameters
- Only 1,457 params for 11,000 training samples = healthy 8:1 ratio


---

## PART 3: SEQUENCES AND TIME

### 3.1 Why Sequences Are Different

Everything above treats each input independently. Feed in an EEG window,
get a PAC estimate. The model has no memory of what came before.

But brain signals have **temporal structure**. PAC at time t depends on
PAC at times t-1, t-2, t-3... If PAC has been declining for the last
10 seconds, it's more likely to continue declining than to suddenly spike.

To predict the FUTURE, we need models that understand SEQUENCES -- ordered
series of data points where the past informs the future.

```
Static model (EEGNet):
  Window at time t  -->  PAC estimate at time t
  (no history, no future)

Sequence model (what we need):
  Windows at times [t-19, t-18, ..., t-1, t]  -->  PAC prediction at time t+5
  (uses 20 seconds of history to predict 5 seconds ahead)
```

Three major approaches to sequence modeling:
1. RNNs / LSTMs / GRUs (process one step at a time)
2. Transformers (attend to all steps at once)
3. TCNs (convolve across time)


### 3.2 RNN: Recurrent Neural Network (The Basic Idea)

An RNN processes a sequence one step at a time, carrying forward a
**hidden state** that summarizes everything it has seen so far.

```
        x1        x2        x3        x4        x5
        |         |         |         |         |
        v         v         v         v         v
h0 --> [RNN] --> [RNN] --> [RNN] --> [RNN] --> [RNN] --> h5 --> output
        |         |         |         |         |
       h1        h2        h3        h4        h5

h = hidden state (a vector of numbers summarizing the past)
x = input at each timestep
```

At each step, the RNN:
1. Takes the current input (x_t) and the previous hidden state (h_{t-1})
2. Computes a new hidden state: h_t = f(W_x * x_t + W_h * h_{t-1} + b)
3. Passes h_t to the next step

The final hidden state h5 theoretically contains a summary of the entire
sequence, which is used to make a prediction.

**The problem:** In practice, basic RNNs have terrible memory. Information
from early timesteps (x1, x2) gets diluted as it passes through many
processing steps. By the time you reach x20, the network has essentially
"forgotten" x1. This is the **vanishing gradient problem** -- during
backpropagation, gradients shrink exponentially as they flow backward
through time, so early timesteps barely get updated.


### 3.3 LSTM: Long Short-Term Memory

LSTMs (Hochreiter & Schmidhuber, 1997) solve the vanishing gradient problem
by adding a **cell state** -- a separate memory highway that runs through
the entire sequence with minimal interference.

```
              FORGET       INPUT        OUTPUT
              GATE         GATE         GATE
               |            |            |
        x_t -->|     x_t -->|     x_t -->|
        h_{t-1}|   h_{t-1}->|   h_{t-1}->|
               v            v            v
            [sigmoid]    [sigmoid]    [sigmoid]
               |            |            |
               v            v            v
C_{t-1} --[x FORGET]--[+ ADD NEW]----> C_t ------>
               |            |            |
               |        [tanh]           |
               |         new             [x]
               |         info            |
               |                         v
               |                        h_t -----> output
```

An LSTM has three **gates** (each is a sigmoid producing values 0-1):

1. **Forget Gate:** "How much of the old memory should I keep?"
   - Output near 0 = forget everything
   - Output near 1 = keep everything
   - Learns to forget irrelevant past information

2. **Input Gate:** "How much of the new information should I store?"
   - Controls what new information gets written to memory
   - Combined with a tanh layer that proposes new candidate values

3. **Output Gate:** "How much of the memory should I reveal right now?"
   - The cell state contains the full memory
   - The output gate decides what part is relevant for the current prediction

**The cell state (C_t) is the key innovation.** It flows through the network
with only linear operations (multiply and add). Gradients flow backward
through it without vanishing. This is what gives LSTMs long-range memory.

**In this project:** An LSTM was tested in `temporal/temporal_model.py`.
It worked, but didn't beat the TCN for our specific problem.


### 3.4 GRU: Gated Recurrent Unit

GRUs (Cho et al., 2014) are a simplified version of LSTMs. Instead of three
gates and a separate cell state, GRUs have two gates and merge the cell
state with the hidden state:

```
        x_t, h_{t-1}
             |
        +---------+
        | RESET   |  "How much past should influence the candidate?"
        | GATE    |  High = use past. Low = ignore past.
        +---------+
             |
        +---------+
        | UPDATE  |  "How much should I update vs. keep old state?"
        | GATE    |  High = keep old. Low = take new.
        +---------+
             |
            h_t --> output
```

GRU = LSTM with fewer parameters. Similar performance in many tasks,
faster to train. Neither was used in the final project -- but a judge
might ask "why not GRU?" and the answer is: "TCNs are better for our
specific requirements (causality, parallelism, multi-scale patterns)."


### 3.5 Problems with RNNs/LSTMs for Our Use Case

Three issues made RNNs/LSTMs suboptimal for this project:

**Problem 1: Sequential Processing**
```
LSTM processes:     x1 --> x2 --> x3 --> x4 --> ... --> x20
                    (must finish x1 before starting x2)
                    
TCN processes:      x1, x2, x3, x4, ..., x20
                    (all at once, in parallel)
```
LSTMs process one timestep at a time. You can't compute the output for
timestep 5 until you've processed timesteps 1 through 4. TCNs process
the entire sequence simultaneously using convolutions. Much faster.

**Problem 2: Bidirectional Temptation**
To improve LSTM performance, people often use **bidirectional** LSTMs --
one LSTM reads the sequence left-to-right, another reads right-to-left,
and they combine. This gives each position information about both past
AND future context.

But in our case, we're making REAL-TIME decisions. At time t, we only
have data up to time t. There is no future data to read. A bidirectional
LSTM would be "cheating" -- using information that wouldn't be available
during deployment. The TCN's causal architecture makes this mistake
impossible by design.

**Problem 3: Gradient Issues in Practice**
Despite the LSTM's gating mechanism, very long sequences still suffer
from gradient degradation. The TCN's residual connections provide a more
direct gradient pathway.


---

## PART 4: TEMPORAL CONVOLUTIONAL NETWORKS (TCNs)

### 4.1 The Core Idea

A TCN applies 1D convolutions ACROSS TIME. Instead of processing the
sequence step by step (like an LSTM), it slides filters across the
entire time dimension at once (like a CNN, but along the time axis
instead of across an image).

```
Input sequence:    [t-19] [t-18] [t-17] [t-16] [t-15] ... [t-1] [t]
                      |      |      |      |      |          |    |
                   [=====conv=====]                               |
                      [=====conv=====]                            |
                         [=====conv=====]                         |
                                              ... sliding across time
```

Each convolutional filter learns a temporal pattern. A filter might learn:
"PAC dropping steadily for 3 consecutive seconds = important signal."


### 4.2 Causal Convolution: No Peeking at the Future

A standard convolution looks at neighbors on BOTH sides:
```
Standard (kernel=3):    output[t] depends on input[t-1], input[t], input[t+1]
                                                                       ^^^^
                                                                    FUTURE!
```

A **causal** convolution only looks at the current and PAST values:
```
Causal (kernel=3):      output[t] depends on input[t-2], input[t-1], input[t]
                                                 ^^^^     ^^^^        ^^^^
                                                 past     past      present
```

This is achieved by **left-only padding** -- adding zeros to the left
of the input so the convolution never reaches into the future:

```
Standard pad:   [0] [data data data data data] [0]    <-- sees future zero
Causal pad:     [0] [0] [data data data data data]    <-- only past
```

In PyTorch code, this is: `F.pad(input, (padding, 0))` -- pad left, not right.

**Why this matters:** In real-time deployment, when making a decision at
time t, we literally don't have data from time t+1 yet. A model that was
trained with access to future data would perform well in testing but fail
in the real world. Causal convolution prevents this by design.


### 4.3 Dilated Convolution: Seeing Far Without Many Parameters

Problem: A kernel of size 3 only looks at 3 consecutive timesteps. To see
20 timesteps into the past, you'd need either a huge kernel (expensive)
or many layers (slow, gradient issues).

Solution: **Dilation.** Insert gaps in the kernel.

```
DILATION = 1 (standard):
  Filter looks at: [t-2] [t-1] [t]     <-- 3 consecutive steps
  "I see 1-second patterns"

DILATION = 2:
  Filter looks at: [t-4]  .  [t-2]  .  [t]     <-- skips every other step
  "I see 2-second patterns"

DILATION = 4:
  Filter looks at: [t-8]  .  .  .  [t-4]  .  .  .  [t]     <-- skips 3
  "I see 4-second patterns"

DILATION = 8:
  Filter looks at: [t-16]  . . . . . . .  [t-8]  . . . . . . .  [t]
  "I see 8-second patterns"
```

By stacking layers with exponentially increasing dilations (1, 2, 4, 8),
the network sees patterns at ALL timescales simultaneously:

```
Layer 4 (d=8):  [. . . . . . . . . . . . . . . . *]  sees 8-second rhythms
Layer 3 (d=4):  [. . . . . . . . *]                   sees 4-second rhythms
Layer 2 (d=2):  [. . . . *]                           sees 2-second rhythms
Layer 1 (d=1):  [. . *]                               sees 1-second rhythms
Input:          [t-19] [t-18] ... [t-1] [t]
```

**Receptive field** = how far back the network can see in total.
Formula: RF = 1 + (kernel_size - 1) * sum(dilations)
         RF = 1 + (3 - 1) * (1 + 2 + 4 + 8)
         RF = 1 + 2 * 15
         RF = 31 timesteps = 31 seconds

With only 4 layers and kernel size 3, we see 31 seconds of history.
An LSTM would need to process all 31 steps sequentially. The TCN
processes them all in parallel.


### 4.4 Residual Connections: Helping Gradients Flow

Each TCN block has a **residual connection** (also called a skip connection):

```
input ----+----> [Conv] --> [Norm] --> [Activation] --> [+] --> output
          |                                             ^
          |                                             |
          +--------- (shortcut: input passed directly) -+
```

The output = processed_input + original_input.

Why? If the convolutional layers learn nothing useful, the block can simply
pass the input through unchanged (via the shortcut). The network can never
get WORSE by adding more layers. This makes deep networks much easier to
train and helps gradients flow backward through many layers.


### 4.5 Normalization Layers

**BatchNorm:** Normalizes across the BATCH dimension. Takes the mean and
variance across all samples in a mini-batch and normalizes.
- Problem: Different patients have different PAC baselines. A batch might
  mix patient A (high PAC) with patient B (low PAC). Averaging them
  destroys individual information.

**GroupNorm(1, C) = Instance Norm:** Normalizes each SAMPLE independently.
Every sample is normalized using its own statistics.
- No dependency on other samples in the batch.
- Preserves individual patient characteristics.
- Stable even with batch size = 1 (important for real-time inference).

Our TCN uses GroupNorm. EEGNet uses BatchNorm (which is fine for EEGNet
because it's doing static estimation, not per-patient adaptation).


### 4.6 Attention Pooling

After the 4 TCN blocks, we have a sequence of 20 processed feature vectors.
We need to collapse this into a single vector for prediction.

Option A: Just take the last timestep. Simple, but might miss important
patterns from earlier in the sequence.

Option B: Average all timesteps. Treats all moments as equally important.

Option C (what we use): **Attention Pooling.** Learn which timesteps matter.

```
Processed sequence:  [h1] [h2] [h3] [h4] ... [h20]    (each is 64-dim)
                       |    |    |    |         |
Attention scores:    [0.02][0.01][0.05][0.03] [0.15]    (learned weights)
                       |    |    |    |         |
Weighted sum:     0.02*h1 + 0.01*h2 + 0.05*h3 + ... + 0.15*h20 = output (64-dim)
```

The attention scores are learned via a small Conv1d(64, 1, 1) followed by
softmax. The network learns to pay more attention to certain timesteps --
perhaps the moment when PAC started declining is more informative than
the steady-state period before it.


### 4.7 Our TCN: The Complete Picture

```
INPUT: 20 timesteps x 73 features
  |
  v
[Linear 73->64 + LayerNorm + SiLU]          <-- Input Projection (4,800 params)
  |
  v
[Transpose to (batch, 64, 20)]              <-- Conv1d expects (batch, channels, time)
  |
  v
[TCN Block 1: Dilation=1, 4,416 params]     <-- Sees 1-second patterns
  | + residual connection
  v
[TCN Block 2: Dilation=2, 4,416 params]     <-- Sees 2-second patterns
  | + residual connection
  v
[TCN Block 3: Dilation=4, 4,416 params]     <-- Sees 4-second patterns
  | + residual connection
  v
[TCN Block 4: Dilation=8, 4,416 params]     <-- Sees 8-second patterns
  | + residual connection
  v
[Attention Pooling, 65 params]              <-- Learn which timesteps matter
  |
  +---------+---------+
  |                   |
  v                   v
[Future Head]    [Delta Head]                <-- Two separate predictions
 4,225 params     4,225 params
  |                   |
  v                   v
Predicted PAC    Predicted PAC
at t+5           CHANGE (delta)

TOTAL: 31,043 parameters
```

Each TCN Block internally:
```
Input --> Causal Pad --> Depthwise Conv1d (k=3, groups=64) --> Pointwise Conv1d (1x1)
      --> GroupNorm(1, 64) --> SiLU --> Dropout(0.1) --> + Input (residual) --> Output
```


---

## PART 5: CONNECTING IT ALL TO THIS PROJECT

### 5.1 The Two-Stage System

Our project has two models working together:

```
STAGE 1: EEGNet (CNN)                    STAGE 2: Causal TCN
Purpose: Estimate CURRENT PAC            Purpose: Predict FUTURE PAC
         from raw EEG                             from feature history

Input:   7 channels x 500 samples        Input:   20 timesteps x 73 features
         (2-second EEG window)                    (20 seconds of history)

Output:  Current PAC estimate            Output:  PAC 5 seconds from now
                                                  + predicted change direction

Params:  1,457                           Params:  31,043
Speed:   < 1 ms                          Speed:   < 3 ms
```

Stage 1 runs every 2 seconds to estimate current brain state.
Stage 2 runs every 1 second to predict future brain state.
The controller uses both to decide: STIMULATE or REST.


### 5.2 Why TCN and Not LSTM?

This is a question judges will likely ask. Here's the complete answer:

```
CRITERION              LSTM                    TCN (our choice)
-----------           ------                   ----------------
Causality             Must manually ensure     Causal by design
                      no bidirectional leak     (left-only padding)

Processing            Sequential               Parallel
                      (step by step)            (all at once)

Multi-scale           Single hidden state       Dilations 1,2,4,8
patterns              tries to encode all       explicitly capture
                      timescales at once        different timescales

Receptive field       Variable, depends on      Fixed, deterministic
                      what the gates "decide"   RF = 31 (you KNOW
                      to remember               how far back it looks)

Parameter             ~15,000 params            31,000 params but
efficiency            for similar capacity      with explicit multi-scale
                                                inductive bias

Training              Vanishing gradients       Residual connections
stability             despite gating            give direct gradient path

Inference speed       Sequential = slow         Parallel = fast
                      on GPU/MPS                (< 3 ms total)
```

**The short answer for judges:** "TCN is causal by design -- it literally
cannot cheat by seeing the future. It processes all timesteps in parallel
for fast inference. And its dilated architecture captures patterns from
1 to 31 seconds simultaneously, while an LSTM compresses everything into
a single hidden state."


### 5.3 Why Not a Transformer?

Transformers (the architecture behind ChatGPT) use **attention** to let
every timestep look at every other timestep.

```
Transformer attention:   t1 <--> t2 <--> t3 <--> t4 ... t20
                         (every position attends to every other)
```

For our project:
1. **Too many parameters:** ~85,000 (3x our TCN). With only 11,000 training
   samples, this overfits badly.
2. **Quadratic cost:** Attention cost is O(T^2). For T=20 it's manageable,
   but it's unnecessary overhead for a short sequence.
3. **No built-in multi-scale:** Transformers learn attention patterns from
   data. Our TCN has multi-scale BUILT IN via dilations -- it doesn't need
   to learn that 1-second and 8-second patterns are both relevant.
4. **Tested it anyway:** In `rigor/experiments/tcn_variants.py`, a
   TransformerTCN variant was tested. It overfitted and didn't beat the TCN.


### 5.4 The Horizon Sweep: Why 5 Seconds?

We tested prediction horizons from 1 to 10 seconds:

```
Horizon    Persistence    Ridge     TCN       Who Wins?     Why?
------     -----------    -----     ---       ----------    ----
1 sec      R2 = 0.760     0.812    0.735     Ridge         PAC barely changes in 1s.
                                                           Just copy the current value.

2 sec      R2 = 0.488     0.542    0.470     Ridge         Still easy for linear models.

3 sec      R2 = 0.234     0.254    0.277     TCN           Autocorrelation fading.
                                              starts       TCN's nonlinearity helps.

5 sec      R2 = -0.267   -0.393    0.254     TCN wins      Baselines COLLAPSE.
                                              big          Negative R2 = worse than
                                                           predicting the mean.

8 sec      R2 = -0.276   -0.211    0.240     TCN           TCN stays positive.

10 sec     R2 = -0.256   -0.212    0.278     TCN           Still positive at 10 seconds.
```

**Persistence baseline:** "PAC in 5 seconds = PAC right now." This works at 1-2s
because PAC is autocorrelated at short lags. By 5 seconds, PAC has changed enough
that this assumption is catastrophically wrong (negative R2).

**Ridge regression:** A linear model. Can't capture the nonlinear dynamics of PAC
evolution. Also collapses at 5+ seconds.

**TCN:** The only model that stays positive. It learned something the linear models
can't -- probably the interaction between stimulation state, PAC trends, and
the nonlinear dynamics of neural habituation.

**Why 5 seconds for the controller:** At 1-2s, you don't need ML -- just copy the
current value. At 5+ seconds, you DO need ML, and that's also the minimum lead
time needed for the controller to smoothly transition between stimulation and rest.


### 5.5 The Controller Decision Loop

Every second, the system runs this loop:

```
1. EEGNet estimates current PAC from the latest 2-second EEG window
2. Feature extractor computes 73 features (spectral + PAC-derived + stim context)
3. Features are appended to a rolling 20-step buffer
4. TCN processes the buffer, predicting PAC at t+5 and the delta
5. Controller decides:

   IF TCN predicts decline (delta < -0.3):
       --> STIMULATE (proactive: prevent the decline before it happens)
   
   ELSE IF TCN predicts rise (delta > +0.3):
       --> REST (proactive: brain is recovering, don't waste stimulation)
   
   ELSE (dead zone, delta between -0.3 and +0.3):
       --> Fall back to reactive z-score:
           z < -0.5: PAC is currently low --> STIMULATE
           z > +0.5: PAC is currently high --> REST

   ALSO: Hysteresis guard -- must stay in current state for 5 seconds
         before switching, to prevent rapid oscillation.
```


### 5.6 Why the Results Are Meaningful

The TCN predictive controller achieves:
- 72.1% alignment (vs 64.5% reactive, vs 45.0% fixed schedule)
- 82.6% of low-PAC windows correctly targeted (vs 51.7% reactive)
- 35/35 patients benefited

**"But R2 = 0.254 doesn't sound great"** -- This is the most important
counterargument to prepare for. Here's why it IS great:

1. At 5 seconds, EVERY other method has NEGATIVE R2. The TCN is the only
   model with positive predictive power at this horizon. +0.254 vs -0.267
   is a +0.52 margin.

2. The prediction doesn't need to be perfect. It needs to be **directionally
   correct** -- is PAC going up or down? Even a noisy prediction of the
   correct direction lets the controller make better-than-chance decisions.

3. When integrated into the controller, the system achieves 92% of the
   theoretical oracle upper bound (30.5 / 33.3 PAC gap). The controller
   is robust to prediction noise because of the dead zone and hysteresis.

4. 35/35 patients benefited. The probability of this by chance (if the
   controller were actually random) is 2^-35 < 0.001. This is not luck.


---

## GLOSSARY OF KEY TERMS (Quick Reference)

| Term | Definition |
|------|-----------|
| **Activation function** | Nonlinear function applied after weighted sum. Makes networks capable of learning complex patterns. |
| **Attention** | Mechanism that learns which parts of the input to focus on. |
| **Backpropagation** | Algorithm to compute gradients for all parameters efficiently using the chain rule. |
| **Batch** | A subset of training data processed together before updating parameters. |
| **Bias** | A constant added to the weighted sum in a neuron. Learned during training. |
| **Causal** | Model that only uses present and past data, never future data. |
| **CNN** | Convolutional Neural Network. Uses sliding filters to detect local patterns. |
| **Convolution** | Sliding a filter across data, computing weighted sums at each position. |
| **Depthwise separable** | Factorized convolution: per-channel filtering + cross-channel mixing. Fewer params. |
| **Dilation** | Gaps in a convolutional filter. Increases receptive field without adding parameters. |
| **Dropout** | Randomly turning off neurons during training to prevent overfitting. |
| **Early stopping** | Halting training when validation performance stops improving. |
| **Epoch** | One complete pass through all training data. |
| **Gradient** | Direction and magnitude of change to reduce loss. Computed via backpropagation. |
| **Gradient clipping** | Capping gradient magnitude to prevent explosive updates. |
| **GRU** | Gated Recurrent Unit. Simplified LSTM with 2 gates instead of 3. |
| **Hidden state** | Internal memory of an RNN/LSTM, updated at each timestep. |
| **Huber loss** | Loss function: quadratic for small errors, linear for large. Robust to outliers. |
| **Layer** | A group of neurons that process data together at the same depth in the network. |
| **Learning rate** | Size of parameter updates. Too high = unstable. Too low = slow. |
| **Loss function** | Measures how wrong the model's prediction is. Training minimizes this. |
| **LSTM** | Long Short-Term Memory. RNN variant with gates and cell state for long-range memory. |
| **MSE** | Mean Squared Error. Average of (prediction - actual)^2. |
| **Neuron** | Basic unit: weighted sum of inputs + activation function = output. |
| **Normalization** | Scaling data to a standard range (e.g., z-score: mean=0, std=1). |
| **Overfitting** | Model memorizes training data noise, fails on new data. |
| **Parameter** | Any number learned during training (weights and biases). |
| **Pooling** | Downsampling operation (e.g., average pool reduces size by half). |
| **R-squared (R2)** | Fraction of variance explained. 1.0=perfect, 0=mean, negative=terrible. |
| **Receptive field** | How far back in time the network can "see" from any output position. |
| **Regularization** | Techniques to prevent overfitting (dropout, weight decay, early stopping). |
| **Residual connection** | Shortcut that adds input directly to output of a layer. Helps gradient flow. |
| **RNN** | Recurrent Neural Network. Processes sequences step by step with a hidden state. |
| **TCN** | Temporal Convolutional Network. Processes sequences with dilated causal convolutions. |
| **Transformer** | Architecture using attention to relate all positions in a sequence. Powerful but large. |
| **Underfitting** | Model too simple to capture the real pattern. Bad on all data. |
| **Validation set** | Data held out from training to monitor overfitting. |
| **Weight** | Multiplier on a connection between neurons. Learned during training. |
| **Weight decay** | Penalty on large weights to prevent overfitting (L2 regularization). |

---

*This guide was written for the Synopsys 2026 Science Fair.
It covers every ML concept needed to understand and present the
Closed-Loop 40 Hz Entrainment project.*
