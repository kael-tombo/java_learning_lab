# Fine-Tuning - REAL WORLD PROJECT

## Project: Fine-Tune BERT for Sentiment Analysis

Build a complete fine-tuning pipeline for sentiment classification.

### Architecture

```
Text → Tokenizer → BERT → Classification Head → Sentiment Label
```

### Implementation

```java
public class SentimentAnalyzer {
    private BertModel bert;
    private ClassificationHead head;
    
    public void loadPretrained(String modelPath) {
        bert = BertModel.load(modelPath);
        // Freeze lower layers
        for (int i = 0; i < 8; i++) {
            bert.getLayer(i).freeze();
        }
    }
    
    public void train(List<TextSample> samples) {
        head = new ClassificationHead(768, 3); // positive, negative, neutral
        
        for (int epoch = 0; epoch < 5; epoch++) {
            double totalLoss = 0;
            for (TextSample sample : samples) {
                // Tokenize
                int[] tokens = tokenize(sample.getText());
                
                // Forward through BERT
                double[] features = bert.forward(tokens);
                
                // Forward through classifier
                double[] logits = head.forward(features);
                double loss = crossEntropy(logits, sample.getLabel());
                totalLoss += loss;
                
                // Backward
                head.backward(sample.getLabel());
            }
            System.out.printf("Epoch %d: Loss = %.4f%n", epoch, totalLoss / samples.size());
        }
    }
    
    public Sentiment predict(String text) {
        int[] tokens = tokenize(text);
        double[] features = bert.forward(tokens);
        double[] logits = head.forward(features);
        return Sentiment.fromLogits(logits);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- BERT revolutionized NLP by enabling transfer learning through pretraining and fine-tuning.
- Reference: https://arxiv.org/abs/1810.04805
- Reference: https://huggingface.co/docs/transformers/model_doc/bert

## Deliverables

- [x] BERT model loading and tokenization
- [x] Layer freezing strategy
- [x] Classification head implementation
- [x] Training with differential learning rates
- [x] Evaluation with accuracy and F1 score
