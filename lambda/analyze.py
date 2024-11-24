from transformers import pipeline
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize Hugging Face sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# Analyze top-performing video data to determine common characteristics
def analyze_top_videos(videos):
    df = pd.DataFrame(videos)
    most_common_topic = df['Topic'].mode()[0]  # Find most common topic
    avg_sentiment_score = df['SentimentScore'].mean()  # Calculate average sentiment score
    top_video_urls = df['URL'].tolist()  # Collect URLs for the top videos
    return most_common_topic, avg_sentiment_score, top_video_urls

# Sentiment analysis function for new video
def analyze_sentiment(text):
    result = sentiment_analyzer(text)[0]
    sentiment = 1 if result['label'] == 'POSITIVE' else -1
    return sentiment * result['score']

# Analyze current video transcript sentiment
video_sentiment = analyze_sentiment(video_transcript)
comment_sentiments = [analyze_sentiment(comment) for comment in comments]
average_comment_sentiment = sum(comment_sentiments) / len(comment_sentiments)

# Analyze top-performing videos for feedback
most_common_topic, avg_top_video_sentiment, top_video_urls = analyze_top_videos(top_videos)
print(f"Most Common Topic in Top Videos: {most_common_topic}")
print(f"Average Sentiment Score in Top Videos: {avg_top_video_sentiment:.2f}")

# Generate tailored feedback based on comparison
feedback = []
if video_sentiment < avg_top_video_sentiment:
    feedback.append("Try to make your video more positive and engaging, as top-performing videos generally have a higher sentiment score.")
if most_common_topic != "Feature Introduction":
    feedback.append(f"Consider creating more content on '{most_common_topic}' topics, as this resonates well with your audience.")
if average_comment_sentiment < video_sentiment:
    feedback.append("Consider addressing viewer concerns noted in comments to improve alignment with audience expectations.")

print("\nFeedback Suggestions:")
for suggestion in feedback:
    print(f"- {suggestion}")

print("\nTop-Performing Video URLs for Inspiration:")
for url in top_video_urls[0:7]:
    print(f"- {url}")

# Convert data to DataFrame for visualization
df_comments = pd.DataFrame({
    'Comment': comments,
    'Sentiment Score': comment_sentiments
})

# Plotting the insights
plt.figure(figsize=(12, 7))
sns.barplot(data=df_comments, x='Comment', y='Sentiment Score', color='skyblue')
plt.axhline(y=video_sentiment, color='red', linestyle='--', label='Current Video Sentiment')
plt.axhline(y=avg_top_video_sentiment, color='green', linestyle='--', label='Avg Top Video Sentiment')
plt.title("Sentiment Comparison: Comments vs. Video and Top Video Average")
plt.ylabel("Sentiment Score")
plt.legend(["Current Video Sentiment", "Average Top Video Sentiment"])
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
