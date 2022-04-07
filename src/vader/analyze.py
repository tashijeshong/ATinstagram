from vaderSentiment.vaderSentiment import NEGATE, SentimentIntensityAnalyzer

if __name__ == '__main__':

    output_file = open("./analysis_output2.txt", "w", encoding="utf8")
    # non_eng_output_file = open("./non_english_caption.txt", "w", encoding="utf8")

    # --- examples -------
    sentences = [
                # "VADER is smart, handsome, and funny.",  # positive sentence example
                # "VADER is very smart, handsome, and funny.",
                "This guy is not smart, handsome, nor funny."  # negation sentence example
                # "The plot was good, but the characters are uncompelling and the dialog is not great.",
                # "Sentiment analysis has never been good.",
                # "Sentiment analysis has never been this good!",
                # "Most automated sentiment analysis tools are shit.",
                # "With VADER, sentiment analysis is the shit!",
                # "Other sentiment analysis tools can be quite bad.",
                # "On the other hand, VADER is quite bad ass",
                # "VADER is such a badass!",  # slang with punctuation emphasis
                # "Without a doubt, excellent idea.",
                # "Roger Dodger is one of the most compelling variations on this theme.",
                # "Roger Dodger is at least compelling as a variation on the theme.",
                # "Roger Dodger is one of the least compelling variations on this theme.",
                # "Not such a badass after all.",  # Capitalized negation with slang
                # "Without a doubt, an excellent idea."  # "without {any} doubt" as negation
                 ]

    analyzer = SentimentIntensityAnalyzer()

    for sentence in sentences:
        # print("list of words are: %s" % analyzer.list_of_words(sentence))
        # print(": %s" % analyzer.list_of_words(sentence))
        words_list = analyzer.list_of_words(sentence)
        score_list = analyzer.scores_of_each_words(sentence)

        # print(words_list)
        # print(score_list)

        output_file.write("Given sentence:: %s\n\n" % sentence)

        lex_words = analyzer.list_of_lexicon_words(words_list)
        output_file.write("Words in lexicon list and their valence scores are: \n")
        for lex in lex_words:
            output_file.write("%s: %.1f\n" % (lex, analyzer.lexicon[lex]))
        output_file.write("<Words with ALL CAPS will have their intensity increased by adjusting their scalar>\n\n")

        # print(lex_words)

        negate_count = 0
        output_file.write("Negation words used: \n")
        for word in words_list:
            if word in NEGATE:
                negate_count += 1
                output_file.write("%s\n" % word)
        if negate_count == 0:
            output_file.write("None\n\n")
        else:
            output_file.write("<These negation words are accounted when calculating valence scores>\n\n")

        output_file.write("Each word in the sentence score with necessary scalar and intensity applied:\n")
        for i in range(len(words_list)):
            output_file.write("%s: %.3f\n" % (words_list[i], score_list[i]))

        output_file.write("\n")
        output_file.write("Normalizing the total score...\n")
        output_file.write("Computing positive, negative, and neutral scores...\n")
        # print(SentimentIntensityAnalyzer.score_valence(score_list, sentence))
        vs = analyzer.polarity_scores(sentence)
        for key, value in vs.items():
            output_file.write("%s score was: %.3f\n" % (key, value))
        
        # need more research on scoring boundary
        total_score = vs["compound"]
        output_file.write("\n")
        if total_score >= 0.5:
            output_file.write("The sentence in overall had positive sentiment with compounding score")
        elif total_score >= 0.25 and total_score < 0.5:
            output_file.write("The sentence in overall had slightly positive sentiment with compounding score")
        elif total_score >= -0.25 and total_score < 0.25:
            output_file.write("The sentence in overall had neutral sentiment with compounding score")
        elif total_score > -0.5 and total_score < -0.25:
            output_file.write("The sentence in overall had slightly negative sentiment with compounding score")
        elif total_score <= -0.5:
            output_file.write("The sentence in overall had negative sentiment with compounding score")
        output_file.write(" %.3f\n" % total_score)
        output_file.write("==============================================================\n\n")

    # print(SentimentIntensityAnalyzer._sift_sentiment_scores(score_list))
    
    output_file.close()