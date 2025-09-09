# Mock knowledge base: small curated corpus with provenance ids.
CORPUS = [
  {
    "id": "kb:nn#1",
    "topic": "neural networks",
    "text": "The main types of neural networks include feedforward networks, convolutional neural networks (CNNs), recurrent neural networks (RNNs), and transformers.",
    "source": "mock:encyclopedia"
  },
  {
    "id": "kb:opt#1",
    "topic": "optimization",
    "text": "Common ML optimization techniques are gradient descent, stochastic gradient descent (SGD), momentum, RMSProp, and Adam.",
    "source": "mock:handbook"
  },
  {
    "id": "kb:transformers#1",
    "topic": "transformers",
    "text": "Transformers use self-attention to model dependencies. They parallelize training well but can be computationally expensive due to quadratic attention.",
    "source": "mock:paper_summary"
  },
  {
    "id": "kb:transformers#2",
    "topic": "transformers",
    "text": "Efficiency techniques include sparse attention, low-rank factorization, linearized attention, and model distillation; trade-offs involve accuracy vs. compute/memory.",
    "source": "mock:survey"
  },
  {
    "id": "kb:rl#1",
    "topic": "reinforcement learning",
    "text": "Recent RL papers explore model-based RL, policy gradients with variance reduction, offline RL datasets, and hierarchical RL for long-horizon tasks.",
    "source": "mock:recent_papers"
  },
  {
    "id": "kb:compare#1",
    "topic": "comparison",
    "text": "For image tasks, CNNs excel at spatial locality; Transformers handle long-range dependencies; RNNs suit sequence modeling with temporal dynamics.",
    "source": "mock:compare_note"
  }
]
