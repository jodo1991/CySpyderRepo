from collections import Counter


# class to implement spaCy nlp and do text analysis
class Analyzer:
    nlp = None

    def __init__(self, updateque):
        # words to exclude from noun phrases nlp finds
        self.exclude_words = {
        '’s':1, 'krebsonsecurity':1, 'threatpost':1, 'darkreading':1, 'reading':1, 'chris gonsalves':1, "its":1,
        'mike mimoso':1, 'chris brook':1, 'dennis fisher':1, 'dark reading':1, 'reuters':1, 'ip':1, 'update':1
    }
        self.updateque = updateque

    # takes a while, allows class to be created and this to be called later
    def loadSpacy(self):
        if Analyzer.nlp is None:
            import spacy
            Analyzer.nlp = spacy.load('en')

    # main processing algorithm
    def getMostCommonNounPhrases(self, maxphrases, articles, stopevent, returntype):
        # indiv keeps track of each article phrases, total is for all articles passed in
        indivMostCommon = Counter()
        totalMostCommon = Counter()
        count = 0
        threads = 8 if len(articles) > 50 else 2
        for doc in Analyzer.nlp.pipe(articles, n_threads=threads, batch_size=int(len(articles)/8)+1):
            if stopevent.is_set():
                break
            count += 1
            if self.updateque.empty() and len(articles) > 1:
                self.updateque.put(int(count*100/len(articles)))


            indivMostCommon.clear()

            # want totalMostCommon to only keep unique phrases from each article..more accurate
            unique = set()
            for phrase in doc.noun_chunks:
                foundproper = False
                propphrase = ''
                strippedphrase = ''
                # only want to keep track of proper nouns that aren't a date time or person
                for word in phrase:
                    if word.text != "'s" and word.ent_type_ not in "DATE TIME PERSON PART" \
                            and word.text.lower() not in self.exclude_words:
                        if word.pos_ == "PROPN":
                            foundproper = True
                            propphrase = (propphrase + ' ' + word.text).strip()

                        if word.pos_ != "DET":
                            strippedphrase = (strippedphrase + ' ' + word.text).strip()

                # found a phrase with a proper noun, now make sure it hasn't been added already
                if foundproper:
                    if propphrase in ["US", "U.S.", "United States"]:
                        propphrase = "United States"
                    foundsimilar = False

                    for commonphrase in indivMostCommon.elements():
                        if propphrase.split()[0] in commonphrase:
                        # if it has been added already, just increase the count
                            newphrase = self.getpropns(commonphrase)
                            if propphrase == newphrase:
                                indivMostCommon.update([commonphrase])
                                unique.add(commonphrase)
                                foundsimilar = True
                                break

                    # otherwise add a new instance of it to the counter
                    if not foundsimilar:
                        indivMostCommon.update([strippedphrase])
                        unique.add(propphrase)

            totalMostCommon.update(unique)

        # handle returning differently based on argument passed in
        if returntype == "one":
            return [phrase for phrase in indivMostCommon.most_common(maxphrases)]
        else:
            return [phrase for phrase in totalMostCommon.most_common(maxphrases)]

    # reduces a phrase down to just proper nouns as sort of an identifier to see if it is in the counter already
    def getpropns(self, phrase):
        doc = Analyzer.nlp(phrase)
        string = ''
        for word in doc:
            if word.pos_ == "PROPN":
                string = (string + ' ' + word.text).strip()

        return string