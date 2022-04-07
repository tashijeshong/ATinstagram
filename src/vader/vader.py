from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    #note: depending on how you installed (e.g., using source code download versus pip install), you may need to import like this:
    #from vaderSentiment import SentimentIntensityAnalyzer

# --- examples -------
sentences = ["VADER is smart, handsome, and funny.",  # positive sentence example
             "VADER is smart, handsome, and funny!",  # punctuation emphasis handled correctly (sentiment intensity adjusted)
             "VADER is very smart, handsome, and funny.", # booster words handled correctly (sentiment intensity adjusted)
             "VADER is VERY SMART, handsome, and FUNNY.",  # emphasis for ALLCAPS handled
             "VADER is VERY SMART, handsome, and FUNNY!!!", # combination of signals - VADER appropriately adjusts intensity
             "VADER is VERY SMART, uber handsome, and FRIGGIN FUNNY!!!", # booster words & punctuation make this close to ceiling for score
             "VADER is not smart, handsome, nor funny.",  # negation sentence example
             "The book was good.",  # positive sentence
             "At least it isn't a horrible book.",  # negated negative sentence with contraction
             "The book was only kind of good.", # qualified positive sentence is handled correctly (intensity adjusted)
             "The plot was good, but the characters are uncompelling and the dialog is not great.", # mixed negation sentence
             "Today SUX!",  # negative slang with capitalization emphasis
             "Today only kinda sux! But I'll get by, lol", # mixed sentiment example with slang and constrastive conjunction "but"
             "Make sure you :) or :D today!",  # emoticons handled
             "Catch utf-8 emoji such as such as 💘 and 💋 and 😁",  # emojis handled
             "Not bad at all",  # Capitalized negation
             "I simply love rivers, the AT has me hiking over/next to several.",
             "Today was amazing. I hiked the hardest trail I’ve ever been on. It was so challenging and kind of life changing… if that makes sense… so many realizations and moments of becoming emotional because of what I have overcame in the last few years. I’m so proud of myself.",
             "Yesterday was one of the hardest days I’ve had on trail. After starting south from Stehekin, I immediately started feeling sharp pain in my left knee after stretching and taking ibuprofen. Going into a 110 mile stretch with no bailout options just didn’t feel right. I decided to say goodbye to my trail family and head back to Stehekin. The plan is to get off trail until I can figure out what’s going on with this injury, even if that means putting it off a year. In just over a week, I met some incredible people and saw some pretty wild things. Crash, Long Way, Piglet, and Donuts - thanks for the miles and the extra push here and there. I’m stoked to see you reach Mexico! Until next time PCT. I’ll be back very soon✌️"
             ]

analyzer = SentimentIntensityAnalyzer()
for sentence in sentences:
    vs = analyzer.polarity_scores(sentence)
    print("{:-<65} {}".format(sentence, str(vs)))