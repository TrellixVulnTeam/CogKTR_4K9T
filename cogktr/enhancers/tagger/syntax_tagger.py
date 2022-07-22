from cogktr.enhancers.tagger import BaseTagger
import stanza


class SyntaxTagger(BaseTagger):
    def __init__(self, tool):
        super().__init__()
        if tool not in ["stanza"]:
            raise ValueError("{} in PosTagger is not supported!".format(tool))

        self.tool = tool
        self.knowledge_type = "syntaxtagger"

        print("Loading SyntaxTagger...")
        if self.tool == "stanza":
            # download stanza use:
            # stanza.download(lang='en', processors='tokenize,mwt,pos,lemma,depparse')
            self.syntaxtagger = stanza.Pipeline(lang='en',
                                                processors='tokenize,mwt,pos,lemma,depparse',
                                                tokenize_pretokenized=True)
        print("Finish loading SyntaxTagger...")

    def tag(self, sentence):
        tag_dict = {}
        if self.tool == "stanza":
            tag_dict = self._stanza_tag(sentence)
        return tag_dict

    def _stanza_tag(self, sentence):
        if isinstance(sentence, str):
            sentence = sentence
        elif isinstance(sentence, list):
            sentence = [sentence]
        else:
            raise ValueError("Sentence must be str or a list of words!")

        tag_dict = {}
        word_list = []
        deprel_list = []
        head_list = []
        indexes_list = []
        pos_list = []
        lemma_list = []

        tag_result = self.syntaxtagger(sentence)
        for word in tag_result.sentences[0].words:
            word_list.append(word.text)
            deprel_list.append(word.deprel)
            head_list.append(word.head)
            indexes_list.append(word.id)
            pos_list.append(word.pos)
            lemma_list.append(word.lemma)
        tag_dict["words"] = word_list
        tag_dict["knowledge"] = {}
        tag_dict["knowledge"]["deprels"] = deprel_list
        tag_dict["knowledge"]["heads"] = head_list
        tag_dict["knowledge"]["indexes"] = indexes_list
        tag_dict["knowledge"]["pos"] = pos_list
        tag_dict["knowledge"]["lemma"] = lemma_list
        return tag_dict


if __name__ == "__main__":
    tagger = SyntaxTagger(tool="stanza")
    tagger_dict_1 = tagger.tag(["Bert", "likes", "reading", "in the Sesame", "Street", "Library."])
    tagger_dict_2 = tagger.tag("Bert likes reading in the Sesame Street Library.")
    print(tagger_dict_1)
    print(tagger_dict_2)
    print("end")
