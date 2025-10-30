![](https://github.com/RYbread0/newzyx/blob/7daf2f6cb1ca0c91f1bdb8fa4e8368d07e995b62/newzyx_logo.png)

# NEWZYX - News podcast for kids & teens

## Congressional App Challenge 2025

### Illinois District 5

### Developed by: Ryan Gupta

---

## 1. Introduction

Newzyx allows kids and teens to listen to and enjoy the news more often. It is an AI-powered news website that automatically finds, summarizes, and creates a podcast for them. It filters out ads, duplicates, and overly complex and inappropriate stories. The goal is to make staying informed fun, safe, and effortless. They get clear, unbiased news, which helps them understand the world and stay curious. Since the product is in the form of a podcast, kids can listen to it in the morning during school drop-offs or any time later in the day. It covers the latest news in areas of science, space, geography, and history.

## 2. Inspiration

I struggled to read the news in the mornings. I thought it was boring, irrelevant, and a waste of time. I didn't want to sit down, go through multiple articles, get biased opinions, and still not fully understand what was going on. I realized that there must be a solution to this. Three years ago, I tried making my first news website; it was fully manual and wasted a lot of time — I did not have the skills back then to make it automated. Research has proven that podcasts and audiobooks are easier and more engaging to consume, fits into everyone's daily routine, build listening and comprehension skills, are more accessible and inclusive, and match modern media habits. There is multiple supporting evidence from Edison Research, National Literacy Trust,

## 3. Features

List and briefly explain the key features of your app. Use bullet points for clarity.

*   Podcast: Relevant, fun, age-appropriate, unbiased 4-7min summary.
*   Website: Brief summary of each article
*   Website: No images or ads to distract and access to the full archive

## 4. Technical Details

### 4.1. Technologies Used

Specify the programming languages, frameworks, and tools utilized in your app's development.

*   **Python and AI engine APIs**
*   **AWS, Squarespace, OpenAI, NewsAPI**

### 4.2. Technical Challenges & Solutions

I faced a major difficulty taking out ads, duplicates, and inappropriate stories. The News API continued to pick up unsuitable headlines, which caused the OpenAI API to provide flawed news. I was able to fix this by having the News API select multiple headlines and then letting the OpenAI API choose the news. Since an AI was picking out the news, this solved the problem. For text-to-speech, I tried to shift to Eleven Labs, which has high-quality audio, but mid-project, I realized the cost was prohibitive, and decided to switch back to OpenAI TTS. I did not have enough time left to run any tests, so there may be common cases where the code can glitch.

