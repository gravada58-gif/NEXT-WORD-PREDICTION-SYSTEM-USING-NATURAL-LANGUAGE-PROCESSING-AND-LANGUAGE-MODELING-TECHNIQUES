"""
Next Word Prediction System
Predicts the next word in a sentence using NLP and language modeling
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

def generate_text_corpus(n_samples=5000, random_state=42):
    """Generate synthetic text corpus for training"""
    np.random.seed(random_state)
    
    # Common sentence patterns
    subjects = ['The cat', 'A dog', 'The student', 'A teacher', 'The company', 'A person', 'The system', 'An application']
    verbs = ['is', 'was', 'has', 'will', 'can', 'should', 'must', 'may']
    adjectives = ['beautiful', 'smart', 'fast', 'efficient', 'reliable', 'innovative', 'powerful', 'user-friendly']
    nouns = ['dog', 'cat', 'book', 'computer', 'system', 'application', 'solution', 'technology']
    adverbs = ['very', 'quite', 'really', 'extremely', 'highly', 'incredibly', 'remarkably', 'absolutely']
    
    sentences = []
    for i in range(n_samples):
        # Generate varied sentence structures
        pattern = np.random.choice(['S-V-A-N', 'S-V-Adv-A', 'A-N-V', 'S-V-N'])
        
        if pattern == 'S-V-A-N':
            sentence = f"{np.random.choice(subjects)} {np.random.choice(verbs)} {np.random.choice(adjectives)} {np.random.choice(nouns)}"
        elif pattern == 'S-V-Adv-A':
            sentence = f"{np.random.choice(subjects)} {np.random.choice(verbs)} {np.random.choice(adverbs)} {np.random.choice(adjectives)}"
        elif pattern == 'A-N-V':
            sentence = f"{np.random.choice(adjectives)} {np.random.choice(nouns)} {np.random.choice(verbs)} {np.random.choice(adjectives)}"
        else:
            sentence = f"{np.random.choice(subjects)} {np.random.choice(verbs)} {np.random.choice(nouns)}"
        
        sentences.append(sentence)
    
    return sentences

def extract_word_sequences(sentences):
    """Extract word sequences and create training data"""
    data = []
    word_to_idx = {}
    idx_to_word = {}
    word_idx = 0
    
    # Build vocabulary
    all_words = set()
    for sentence in sentences:
        words = sentence.lower().split()
        all_words.update(words)
    
    for word in sorted(all_words):
        word_to_idx[word] = word_idx
        idx_to_word[word_idx] = word
        word_idx += 1
    
    # Extract sequences
    for sentence in sentences:
        words = sentence.lower().split()
        
        # Create n-grams (bigrams and trigrams)
        for i in range(len(words) - 1):
            prev_word = words[i]
            next_word = words[i + 1]
            
            # Calculate word frequency in sentence
            word_freq = Counter(words)
            
            # Calculate sentence length
            sentence_length = len(words)
            
            # Calculate word position
            word_position = i / len(words)
            
            # Calculate word length
            prev_word_length = len(prev_word)
            next_word_length = len(next_word)
            
            # Calculate vowel ratio
            vowels = 'aeiou'
            prev_vowel_ratio = sum(1 for c in prev_word if c in vowels) / len(prev_word) if len(prev_word) > 0 else 0
            next_vowel_ratio = sum(1 for c in next_word if c in vowels) / len(next_word) if len(next_word) > 0 else 0
            
            data.append({
                'Sentence_ID': sentences.index(sentence),
                'Previous_Word': prev_word,
                'Next_Word': next_word,
                'Word_Frequency': word_freq[prev_word],
                'Sentence_Length': sentence_length,
                'Word_Position': word_position,
                'Prev_Word_Length': prev_word_length,
                'Next_Word_Length': next_word_length,
                'Prev_Vowel_Ratio': prev_vowel_ratio,
                'Next_Vowel_Ratio': next_vowel_ratio,
                'Next_Word_Index': word_to_idx[next_word]
            })
    
    df = pd.DataFrame(data)
    return df, word_to_idx, idx_to_word

def prepare_features(df):
    """Prepare features for modeling"""
    df_copy = df.copy()
    
    feature_cols = ['Word_Frequency', 'Sentence_Length', 'Word_Position', 
                   'Prev_Word_Length', 'Next_Word_Length', 'Prev_Vowel_Ratio', 'Next_Vowel_Ratio']
    
    X = df_copy[feature_cols]
    y = df_copy['Next_Word_Index']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    return X_scaled, y, scaler

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple prediction models"""
    from sklearn.model_selection import train_test_split
    
    models = {}
    results = []
    predictions = {}
    
    # Logistic Regression
    print("Training Logistic Regression...")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    
    models['Logistic Regression'] = lr
    predictions['Logistic Regression'] = y_pred_lr
    results.append({
        'Model': 'Logistic Regression',
        'Accuracy': accuracy_score(y_test, y_pred_lr),
        'Precision': precision_score(y_test, y_pred_lr, average='weighted', zero_division=0),
        'Recall': recall_score(y_test, y_pred_lr, average='weighted', zero_division=0),
        'F1_Score': f1_score(y_test, y_pred_lr, average='weighted', zero_division=0)
    })
    
    # Random Forest
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    models['Random Forest'] = rf
    predictions['Random Forest'] = y_pred_rf
    results.append({
        'Model': 'Random Forest',
        'Accuracy': accuracy_score(y_test, y_pred_rf),
        'Precision': precision_score(y_test, y_pred_rf, average='weighted', zero_division=0),
        'Recall': recall_score(y_test, y_pred_rf, average='weighted', zero_division=0),
        'F1_Score': f1_score(y_test, y_pred_rf, average='weighted', zero_division=0)
    })
    
    # SVM
    print("Training SVM...")
    svm = SVC(kernel='rbf', random_state=42)
    svm.fit(X_train, y_train)
    y_pred_svm = svm.predict(X_test)
    
    models['SVM'] = svm
    predictions['SVM'] = y_pred_svm
    results.append({
        'Model': 'SVM',
        'Accuracy': accuracy_score(y_test, y_pred_svm),
        'Precision': precision_score(y_test, y_pred_svm, average='weighted', zero_division=0),
        'Recall': recall_score(y_test, y_pred_svm, average='weighted', zero_division=0),
        'F1_Score': f1_score(y_test, y_pred_svm, average='weighted', zero_division=0)
    })
    
    return models, pd.DataFrame(results), predictions, y_test

def plot_word_distribution(df):
    """Plot word distribution"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    prev_word_counts = df['Previous_Word'].value_counts().head(15)
    next_word_counts = df['Next_Word'].value_counts().head(15)
    
    axes[0].barh(prev_word_counts.index, prev_word_counts.values, color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_xlabel('Frequency', fontsize=11, fontweight='bold')
    axes[0].set_title('Top 15 Previous Words', fontsize=12, fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)
    
    axes[1].barh(next_word_counts.index, next_word_counts.values, color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_xlabel('Frequency', fontsize=11, fontweight='bold')
    axes[1].set_title('Top 15 Next Words', fontsize=12, fontweight='bold')
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/word_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: word_distribution.png")
    plt.close()

def plot_model_comparison(results_df):
    """Plot model performance comparison"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1_Score']
    
    for idx, metric in enumerate(metrics):
        row = idx // 2
        col = idx % 2
        
        axes[row, col].bar(results_df['Model'], results_df[metric], color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        axes[row, col].set_ylabel(metric, fontsize=11, fontweight='bold')
        axes[row, col].set_title(f'{metric} Comparison', fontsize=12, fontweight='bold')
        axes[row, col].set_ylim([0, 1.1])
        axes[row, col].grid(axis='y', alpha=0.3)
        axes[row, col].tick_params(axis='x', rotation=45)
        
        for i, v in enumerate(results_df[metric]):
            axes[row, col].text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/prediction_model_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: prediction_model_comparison.png")
    plt.close()

def plot_feature_importance(models):
    """Plot feature importance"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Random Forest
    rf_model = models['Random Forest']
    feature_names = ['Word_Frequency', 'Sentence_Length', 'Word_Position', 
                    'Prev_Word_Length', 'Next_Word_Length', 'Prev_Vowel_Ratio', 'Next_Vowel_Ratio']
    importances = rf_model.feature_importances_
    
    sorted_idx = np.argsort(importances)[::-1]
    axes[0].barh(np.array(feature_names)[sorted_idx], importances[sorted_idx], color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[0].set_title('Random Forest Feature Importance', fontsize=12, fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)
    
    # Logistic Regression coefficients
    lr_model = models['Logistic Regression']
    coef_mean = np.abs(lr_model.coef_).mean(axis=0)
    sorted_idx = np.argsort(coef_mean)[::-1]
    
    axes[1].barh(np.array(feature_names)[sorted_idx], coef_mean[sorted_idx], color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_xlabel('Coefficient Magnitude', fontsize=11, fontweight='bold')
    axes[1].set_title('Logistic Regression Feature Importance', fontsize=12, fontweight='bold')
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/prediction_feature_importance.png', dpi=300, bbox_inches='tight')
    print("Saved: prediction_feature_importance.png")
    plt.close()

def plot_prediction_analysis(df):
    """Plot prediction analysis"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    
    # Sentence length distribution
    axes[0, 0].hist(df['Sentence_Length'], bins=20, color='#3498db', alpha=0.7, edgecolor='black', linewidth=1.5)
    axes[0, 0].set_xlabel('Sentence Length', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Sentence Length Distribution', fontsize=12, fontweight='bold')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Word position distribution
    axes[0, 1].hist(df['Word_Position'], bins=20, color='#2ecc71', alpha=0.7, edgecolor='black', linewidth=1.5)
    axes[0, 1].set_xlabel('Word Position (Normalized)', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Word Position Distribution', fontsize=12, fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Word frequency distribution
    axes[1, 0].hist(df['Word_Frequency'], bins=20, color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.5)
    axes[1, 0].set_xlabel('Word Frequency', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Word Frequency Distribution', fontsize=12, fontweight='bold')
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Vowel ratio distribution
    axes[1, 1].hist(df['Prev_Vowel_Ratio'], bins=20, color='#f39c12', alpha=0.7, edgecolor='black', linewidth=1.5, label='Previous Word')
    axes[1, 1].hist(df['Next_Vowel_Ratio'], bins=20, color='#9b59b6', alpha=0.5, edgecolor='black', linewidth=1.5, label='Next Word')
    axes[1, 1].set_xlabel('Vowel Ratio', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Vowel Ratio Distribution', fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/prediction_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: prediction_analysis.png")
    plt.close()

def main():
    print("="*80)
    print("NEXT WORD PREDICTION SYSTEM")
    print("="*80)
    
    # Generate corpus
    print("\n[1] Generating text corpus...")
    sentences = generate_text_corpus(n_samples=5000)
    print(f"Corpus generated: {len(sentences)} sentences")
    
    # Extract sequences
    print("\n[2] Extracting word sequences...")
    df, word_to_idx, idx_to_word = extract_word_sequences(sentences)
    df.to_csv('/home/ubuntu/word_prediction_data.csv', index=False)
    print(f"Sequences extracted: {len(df)} word pairs")
    print(f"Vocabulary size: {len(word_to_idx)}")
    
    # Prepare features
    print("\n[3] Preparing features...")
    X, y, scaler = prepare_features(df)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    
    # Train models
    print("\n[4] Training prediction models...")
    models, results_df, predictions, y_test = train_models(X_train, X_test, y_train, y_test)
    results_df.to_csv('/home/ubuntu/prediction_model_results.csv', index=False)
    print("\nModel Results:")
    print(results_df.to_string(index=False))
    
    # Generate visualizations
    print("\n[5] Generating visualizations...")
    plot_word_distribution(df)
    plot_model_comparison(results_df)
    plot_feature_importance(models)
    plot_prediction_analysis(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All visualizations saved")
    print("="*80)

if __name__ == "__main__":
    main()
