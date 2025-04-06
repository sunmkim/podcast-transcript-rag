# Data Preparation

The data is based off of a transcript from the New York Times podcast *The Daily*. 

More specifically, I used the transcript from its [March 13, 2025 episode](https://www.nytimes.com/2025/03/13/podcasts/the-daily/canada-trade-war-trump.html) titled *Elbows Up: Canada’s Response to Trump’s Trade War*. You can click on the Transcript button and this should a display with the transcript of the episode. I copy-pasted this into Microsoft Word and did some cleaning and formatting.

I removed all the non-utterance text such as the title and subheading, and made sure that the speaker was in a different style format from the text so we can disambiguate between the speaker and the utterance of the said speaker.

This was converted into a list of Python dictionaries with 2 key-values: `speaker` and `utterance`.